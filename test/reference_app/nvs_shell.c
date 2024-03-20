#include <zephyr/drivers/flash.h>
#include <zephyr/fs/nvs.h>
#include <zephyr/shell/shell.h>
#include <zephyr/storage/flash_map.h>

#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>

#define NVS_PARTITION storage_partition
#define NVS_PARTITION_DEVICE FIXED_PARTITION_DEVICE(NVS_PARTITION)
#define NVS_PARTITION_OFFSET FIXED_PARTITION_OFFSET(NVS_PARTITION)

static struct nvs_fs fs;

static int init(const struct shell *shell_ptr)
{
    static bool initialized = false;
    if (initialized)
    {
        return 0;
    }

    struct flash_pages_info info;

    fs.flash_device = NVS_PARTITION_DEVICE;
    if (!device_is_ready(fs.flash_device))
    {
        shell_error(shell_ptr, "Flash device %s is not ready\n", fs.flash_device->name);
        return -EIO;
    }
    fs.offset = NVS_PARTITION_OFFSET;
    if (flash_get_page_info_by_offs(fs.flash_device, fs.offset, &info))
    {
        shell_error(shell_ptr, "Unable to get page info\n");
        return -EIO;
    }
    fs.sector_size = info.size;
    fs.sector_count = 3U;

    if (nvs_mount(&fs))
    {
        shell_error(shell_ptr, "Flash Init failed\n");
        return -EIO;
    }

    initialized = true;
    return 0;
}

static int cmd_read(const struct shell *shell_ptr, size_t argc, char *argv[])
{
    if (init(shell_ptr) < 0)
    {
        shell_error(shell_ptr, "NVS initialization failed");
    }

    uint32_t id = strtoul(argv[1], NULL, 16);
    if (id > UINT16_MAX)
    {
        shell_error(shell_ptr, "Invalid id value");
        return -ENOENT;
    }
    shell_info(shell_ptr, "Reading NVS item ID: %d", id);

    ssize_t bytesRead = 0;
    uint8_t bytes[CONFIG_SHELL_CMD_BUFF_SIZE / 2] = {0};
    bytesRead = nvs_read(&fs, id, bytes, sizeof(bytes));
    if (bytesRead < 0)
    {
        shell_error(shell_ptr, "Failed to read nvs: %d", (int)bytesRead);
        return bytesRead;
    }

    shell_hexdump(shell_ptr, bytes, bytesRead);
    return 0;
}

static int cmd_write(const struct shell *shell_ptr, size_t argc, char *argv[])
{
    if (init(shell_ptr) < 0)
    {
        shell_error(shell_ptr, "NVS initialization failed");
    }

    uint32_t id = strtoul(argv[1], NULL, 16);
    if (id > UINT16_MAX)
    {
        shell_error(shell_ptr, "Invalid id value");
        return -ENOENT;
    }

    uint8_t bytes[CONFIG_SHELL_CMD_BUFF_SIZE / 2] = {0};
    size_t bytes_len = 0;

    bytes_len = hex2bin(argv[2], strlen(argv[2]), bytes, sizeof(bytes));
    if (bytes_len == 0)
    {
        shell_error(shell_ptr, "Failed to parse value");
        return -EINVAL;
    }

    shell_info(shell_ptr, "Writing NVS item ID: %d", id);

    ssize_t bytesWritten = 0;
    bytesWritten = nvs_write(&fs, id, bytes, bytes_len);

    if (bytesWritten < 0)
    {
        shell_error(shell_ptr, "Failed to write to nvs: %d", (int)bytesWritten);
        return bytesWritten;
    }
    else
    {
        shell_info(shell_ptr, "%d bytes written", (int)bytesWritten);
        return 0;
    }
}

static int cmd_delete(const struct shell *shell_ptr, size_t argc, char *argv[])
{
    if (init(shell_ptr) < 0)
    {
        shell_error(shell_ptr, "NVS initialization failed");
    }

    uint32_t id = strtoul(argv[1], NULL, 16);
    if (id > UINT16_MAX)
    {
        shell_error(shell_ptr, "Invalid id value");
        return -ENOENT;
    }
    int ret = nvs_delete(&fs, id);
    if (ret < 0)
    {
        shell_error(shell_ptr, "Failed to delete item from nvs: %d", (int)ret);
        return ret;
    }
    shell_info(shell_ptr, "Deleted NVS item ID: %d", id);
    return 0;
}

SHELL_STATIC_SUBCMD_SET_CREATE(nvs_cmds,
                               SHELL_CMD_ARG(read, NULL,
                                             "Read a specific nvs entry\n"
                                             "Usage: nvs read <id>\n"
                                             "id type: hex",
                                             cmd_read, 2, 0),
                               SHELL_CMD_ARG(write, NULL,
                                             "Write a specific nvs entry\n"
                                             "Usage: nvs write <id> <value>\n"
                                             "id type: hex\n"
                                             "value type: hex",
                                             cmd_write, 3, 0),
                               SHELL_CMD_ARG(delete, NULL,
                                             "Delete a specific nvs entry\n"
                                             "Usage: nvs delete <id>\n"
                                             "id type: hex\n",
                                             cmd_delete, 2, 0),
                               SHELL_SUBCMD_SET_END);

static int cmd_nvs(const struct shell *shell_ptr, size_t argc, char **argv)
{
    shell_error(shell_ptr, "%s unknown parameter: %s", argv[0], argv[1]);
    return -EINVAL;
}

SHELL_CMD_ARG_REGISTER(nvs, &nvs_cmds, "Nvs shell commands",
                       cmd_nvs, 2, 0);
