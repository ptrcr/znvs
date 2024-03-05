#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/flash.h>
#include <zephyr/storage/flash_map.h>
#include <zephyr/fs/nvs.h>

static struct nvs_fs fs;

#define NVS_PARTITION storage_partition
#define NVS_PARTITION_DEVICE FIXED_PARTITION_DEVICE(NVS_PARTITION)
#define NVS_PARTITION_OFFSET FIXED_PARTITION_OFFSET(NVS_PARTITION)

#define ITEM_ID_1 1
#define ITEM_ID_2 2
#define ITEM_ID_3 3

int main(void)
{
    struct flash_pages_info info;

    fs.flash_device = NVS_PARTITION_DEVICE;
    if (!device_is_ready(fs.flash_device))
    {
        printk("Flash device %s is not ready\n", fs.flash_device->name);
        return 0;
    }
    fs.offset = NVS_PARTITION_OFFSET;
    if (flash_get_page_info_by_offs(fs.flash_device, fs.offset, &info))
    {
        printk("Unable to get page info\n");
        return 0;
    }
    fs.sector_size = info.size;
    fs.sector_count = 3U;

    if (nvs_mount(&fs))
    {
        printk("Flash Init failed\n");
        return 0;
    }

    printk("sector count %d\n", fs.sector_count);
    printk("sector size %d\n", fs.sector_size);
    printk("ate wra %d\n", fs.ate_wra);
    // Prepare dummy data
    uint8_t item_1[8] = {0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88};
    uint8_t item_2[12] = {0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A};
    uint8_t item_3[128] = {0};
    for (int n = 0; n < sizeof(item_3); n++)
    {
        item_3[n] = n;
    }

    (void)nvs_write(&fs, ITEM_ID_1, &item_1, sizeof(item_1));
    (void)nvs_write(&fs, ITEM_ID_2, &item_2, sizeof(item_2));
    (void)nvs_write(&fs, ITEM_ID_3, &item_3, sizeof(item_3));

    return 0;
}
