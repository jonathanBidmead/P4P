/* Blink Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "sdkconfig.h"

#include <string.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"
#include "freertos/event_groups.h"
#include "freertos/event_groups.h"
#include "esp_wifi.h"
#include "esp_wpa2.h"
#include "esp_event_loop.h"
#include "esp_log.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "tcpip_adapter.h"

#include "lwip/sockets.h"
#include "lwip/dns.h"
#include "lwip/netdb.h"

#include "mqtt_client.h"

#include "driver/uart.h"
#include "soc/uart_struct.h"
static const int RX_BUF_SIZE = 512;

const static int CONNECTED_BIT = BIT0;

/* Can run 'make menuconfig' to choose the GPIO to blink,
   or you can edit the following line and set a number here.
*/
#define BLINK_GPIO (gpio_num_t)13

/* The examples use simple WiFi configuration that you can set via
   'make menuconfig'.
   If you'd rather not, just change the below entries to strings with
   the config you want - ie #define WPA2_SSID "mywifissid"
   You can choose EAP method via 'make menuconfig' according to the
   configuration of AP.
*/
#define WPA2_SSID "UoA-WiFi"
//#define EXAMPLE_EAP_METHOD CONFIG_EAP_METHOD

#define WPA2_EAP_ID "YourUoaUpi"
#define WPA2_EAP_USERNAME "YourUoaUpi"
#define WPA2_EAP_PASSWORD "YourUoaPassword"

#define USE_WPA2 1 //1 if you want uni network. 0 if you want hotspot/normal network

#define PER_SSID "HotspotSSID"
#define PER_PASSWORD "HotspotPassword"

#define ROBOT_NAME "KR10"

/* FreeRTOS event group to signal when we are connected & ready to make a request */
static EventGroupHandle_t wifi_event_group;

/* The event group allows multiple bits for each event,
   but we only care about one event - are we connected
   to the AP with an IP? */
//const int CONNECTED_BIT = BIT0;

/* Constants that aren't configurable in menuconfig */
#define EAP_PEAP 1
#define EAP_TTLS 2
#define EXAMPLE_EAP_METHOD EAP_PEAP

#define TXD_PIN (GPIO_NUM_17)
#define RXD_PIN (GPIO_NUM_16)
esp_mqtt_client_handle_t mqtt_client = NULL;

static const char *TAG = "example";
bool newPosToMQTT = false;
bool to_tx_available = false;

struct kvas_packet
{
    float command;
    float v1;
    float v2;
    float v3;
    float v4;
    float v5;
    float v6;
    float v7;
    float chksum;
};

kvas_packet to_tx;
kvas_packet to_mqtt;

#define byte uint8_t

byte rec_bytes[36];

static esp_err_t mqtt_event_handler(esp_mqtt_event_handle_t event)
{
    esp_mqtt_client_handle_t client = event->client;
    int msg_id;
    int data_len = event->data_len;
    int topic_len = event->topic_len;
    // your_context_t *context = event->context;

    //float floaters[]={1,2,3,4,5,6,7,8};

    switch (event->event_id)
    {
    case MQTT_EVENT_CONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_CONNECTED");
        msg_id = esp_mqtt_client_subscribe(client, "/kvas/" ROBOT_NAME "c_ax", 0);
        ESP_LOGI(TAG, "sent subscribe successful, msg_id=%d", msg_id);

        msg_id = esp_mqtt_client_subscribe(client, "/kvas/" ROBOT_NAME "/c_pos", 0);
        ESP_LOGI(TAG, "sent subscribe successful, msg_id=%d", msg_id);

        mqtt_client = client;
        msg_id = esp_mqtt_client_publish(client, "/topic/qos0", "Kvas/" ROBOT_NAME " is alive!", 0, 0, 0);
        ESP_LOGI(TAG, "sent publish successful, msg_id=%d", msg_id);

        //byte bytes[32];
        //memcpy(&bytes,&floats,32);
        //msg_id = esp_mqtt_client_publish(client, "/kvas/c_pos",(const char*) &floaters, 32, 0, 0);

        break;
    case MQTT_EVENT_DISCONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_DISCONNECTED");
        break;

    case MQTT_EVENT_SUBSCRIBED:
        ESP_LOGI(TAG, "MQTT_EVENT_SUBSCRIBED, msg_id=%d", event->msg_id);
        //msg_id = esp_mqtt_client_publish(client, "/topic/qos0", "data", 0, 0, 0);
        //ESP_LOGI(TAG, "sent publish successful, msg_id=%d", msg_id);
        break;
    case MQTT_EVENT_UNSUBSCRIBED:
        ESP_LOGI(TAG, "MQTT_EVENT_UNSUBSCRIBED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_PUBLISHED:
        ESP_LOGI(TAG, "MQTT_EVENT_PUBLISHED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_DATA:
        ESP_LOGI(TAG, "MQTT_EVENT_DATA");
        //printf("TOPIC=%.*s\r\n", event->topic_len, event->topic);
        //printf("DATA=%.*s\r\n", event->data_len, event->data);
        ESP_LOGI(TAG, "Topic length %i, Data length %i", topic_len, event->data_len);

        if (topic_len == 15)
        {
            if (data_len == sizeof(to_tx))
            {
                to_tx_available = true;
                memcpy(&to_tx, event->data, data_len);
            }
        }
        else if (topic_len == 16)
        {
            if (data_len == sizeof(to_tx))
            {
                to_tx_available = true;
                memcpy(&to_tx, event->data, data_len);
                memcpy(&rec_bytes, event->data, data_len);
            }
        }

        for (size_t i = 0; i < event->data_len; i++)
        {
            //  printf("DATA[%i]=%i\n",i,rec_bytes[i]);
        }
        if (false)
        {
            /* code */

            printf("To_TX=%f\n", to_tx.command);
            printf("To_TX=%f\n", to_tx.v1);
            printf("To_TX=%f\n", to_tx.v2);
            printf("To_TX=%f\n", to_tx.v3);
            printf("To_TX=%f\n", to_tx.v4);
            printf("To_TX=%f\n", to_tx.v5);
            printf("To_TX=%f\n", to_tx.v6);
            printf("To_TX=%f\n", to_tx.v7);
            printf("To_TX=%f\n", to_tx.chksum);
            printf("End of sectionsubscribe.\n");
        }

        break;
    case MQTT_EVENT_ERROR:
        ESP_LOGI(TAG, "MQTT_EVENT_ERROR");
        break;

    case MQTT_EVENT_BEFORE_CONNECT:
        break;
    }
    return ESP_OK;
}

static void mqtt_app_start(void)
{
    esp_mqtt_client_config_t mqtt_cfg = {};
    mqtt_cfg.uri = "mqtt://127.0.0.1:1883",
    mqtt_cfg.event_handle = mqtt_event_handler;
    mqtt_cfg.username = "kvas";
    mqtt_cfg.password = "pwd";
    mqtt_cfg.client_id = "id";

    esp_mqtt_client_handle_t client = esp_mqtt_client_init(&mqtt_cfg);
    esp_mqtt_client_start(client);
}

static esp_err_t event_handler(void *ctx, system_event_t *event)
{
    switch (event->event_id)
    {
    case SYSTEM_EVENT_STA_START:
        esp_wifi_connect();
        break;
    case SYSTEM_EVENT_STA_GOT_IP:
        xEventGroupSetBits(wifi_event_group, CONNECTED_BIT);
        break;
    case SYSTEM_EVENT_STA_DISCONNECTED:
        esp_wifi_connect();
        xEventGroupClearBits(wifi_event_group, CONNECTED_BIT);
        break;
    default:
        break;
    }
    return ESP_OK;
}

static void initialise_wifi(void)
{
    //unsigned int ca_pem_bytes = ca_pem_end - ca_pem_start;
    //unsigned int client_crt_bytes = client_crt_end - client_crt_start;
    //unsigned int client_key_bytes = client_key_end - client_key_start;

    ///esp_wpa2_config_t config_wpa2 = WPA2_CONFIG_INIT_DEFAULT();

    tcpip_adapter_init();
    wifi_event_group = xEventGroupCreate();
    ESP_ERROR_CHECK(esp_event_loop_init(event_handler, NULL));
    wifi_init_config_t init_cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&init_cfg));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    //esp_wpa2_config_t config = WPA2_CONFIG_INIT_DEFAULT();
    wifi_config_t wifi_config = {};

#if USE_WPA2
    strcpy((char *)wifi_config.sta.ssid, WPA2_SSID);
    strcpy((char *)wifi_config.sta.password, WPA2_EAP_PASSWORD);
#else
    strcpy((char *)wifi_config.sta.ssid, PER_SSID);
    strcpy((char *)wifi_config.sta.password, PER_PASSWORD);
#endif

    //wifi_config_t wifi_config=WIFI_INIT_CONFIG_DEFAULT();
    // = {
    //   .sta = {
    //       .ssid = WPA2_SSID,
    //   },
    //};
    //wifi_config.sta.ssid=WPA2_SSID;
    //ESP_LOGI(TAG, "Setting WiFi configuration SSID %s...", wifi_config.sta.ssid);
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(ESP_IF_WIFI_STA, &wifi_config));
    //ESP_ERROR_CHECK( esp_wifi_sta_wpa2_ent_set_ca_cert(ca_pem_start, ca_pem_bytes) );
    //ESP_ERROR_CHECK( esp_wifi_sta_wpa2_ent_set_cert_key(client_crt_start, client_crt_bytes,
    //		client_key_start, client_key_bytes, NULL, 0) );

#if USE_WPA2
    ESP_ERROR_CHECK(esp_wifi_sta_wpa2_ent_set_identity((uint8_t *)WPA2_EAP_ID, strlen(WPA2_EAP_ID)));
    if (EXAMPLE_EAP_METHOD == EAP_PEAP || EXAMPLE_EAP_METHOD == EAP_TTLS)
    {
        ESP_ERROR_CHECK(esp_wifi_sta_wpa2_ent_set_username((uint8_t *)WPA2_EAP_USERNAME, strlen(WPA2_EAP_USERNAME)));
        ESP_ERROR_CHECK(esp_wifi_sta_wpa2_ent_set_password((uint8_t *)WPA2_EAP_PASSWORD, strlen(WPA2_EAP_PASSWORD)));
    }
    //ESP_ERROR_CHECK( esp_wifi_sta_wpa2_ent_enable(&config_wpa2) );
    ESP_ERROR_CHECK(esp_wifi_sta_wpa2_ent_enable());
#endif
    ESP_ERROR_CHECK(esp_wifi_start());

    while (1)
    {
        tcpip_adapter_ip_info_t ip;
        memset(&ip, 0, sizeof(tcpip_adapter_ip_info_t));
        vTaskDelay(1000 / portTICK_PERIOD_MS);

        if (tcpip_adapter_get_ip_info(TCPIP_ADAPTER_IF_STA, &ip) == 0)
        {
            ESP_LOGI(TAG, "~~~~~~~~~~~");
            ESP_LOGI(TAG, "IP:" IPSTR, IP2STR(&ip.ip));
            ESP_LOGI(TAG, "MASK:" IPSTR, IP2STR(&ip.netmask));
            ESP_LOGI(TAG, "GW:" IPSTR, IP2STR(&ip.gw));
            ESP_LOGI(TAG, "~~~~~~~~~~~");
            break;
        }
    }
}

static void wpa2_enterprise_example_task(void *pvParameters)
{
    tcpip_adapter_ip_info_t ip;
    memset(&ip, 0, sizeof(tcpip_adapter_ip_info_t));
    vTaskDelay(2000 / portTICK_PERIOD_MS);

    while (1)
    {
        vTaskDelay(2000 / portTICK_PERIOD_MS);

        if (tcpip_adapter_get_ip_info(TCPIP_ADAPTER_IF_STA, &ip) == 0)
        {
            ESP_LOGI(TAG, "~~~~~~~~~~~");
            ESP_LOGI(TAG, "IP:" IPSTR, IP2STR(&ip.ip));
            ESP_LOGI(TAG, "MASK:" IPSTR, IP2STR(&ip.netmask));
            ESP_LOGI(TAG, "GW:" IPSTR, IP2STR(&ip.gw));
            ESP_LOGI(TAG, "~~~~~~~~~~~");
        }
    }
}

int sendData_Debug(const char *logName, const char *data)
{
    const int len = strlen(data);
    int txBytes;
    static const bool use_pause_insteaf_of_newline = true;
    if (use_pause_insteaf_of_newline)
    {
        txBytes = uart_write_bytes(UART_NUM_0, data, len);
        txBytes += uart_write_bytes(UART_NUM_0, "\n", 1);
    }
    else
    {
        txBytes = uart_write_bytes_with_break(UART_NUM_0, data, len, 1);
    }

    ESP_LOGI(logName, "Wrote %d bytes", txBytes);
    return txBytes;
}
int sendData(const char *data, const int len)
{
    //const int len = strlen(data);
    int txBytes;
    static const bool use_pause_instead_of_newline = true;
    if (use_pause_instead_of_newline)
    {
        txBytes = uart_write_bytes(UART_NUM_0, data, len);
        txBytes += uart_write_bytes(UART_NUM_0, "\n", 1);
    }
    else
    {
        txBytes = uart_write_bytes_with_break(UART_NUM_0, data, len, 1);
    }

    return txBytes;
}

static void tx_task(void *pvParameter)
{
    static const char *TX_TASK_TAG = "TX_TASK";
    esp_log_level_set(TX_TASK_TAG, ESP_LOG_INFO);
    while (1)
    {
        if (to_tx_available)
        {
            ESP_LOGI(TAG, "New TX was available");
            to_tx_available = false;
            auto ptr = &to_tx;
            sendData((const char *)ptr, 36);
        }
        vTaskDelay(10 / portTICK_PERIOD_MS);
    }
}

void uart_init()
{
    uart_config_t uart_config{};
    uart_config.baud_rate = 115200;
    uart_config.data_bits = UART_DATA_8_BITS;
    uart_config.parity = UART_PARITY_DISABLE;
    uart_config.stop_bits = UART_STOP_BITS_1;
    uart_config.flow_ctrl = UART_HW_FLOWCTRL_DISABLE;

    uart_driver_install(UART_NUM_0, RX_BUF_SIZE * 2, 0, 0, NULL, 0);
    uart_param_config(UART_NUM_0, &uart_config);
    //uart_set_pin(UART_NUM_1, TXD_PIN, RXD_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
    // We won't use a buffer for sending data.
}

void mqtt_sendposition(const char *data)
{
    if (!mqtt_client)
    {
        return;
    }
    if (data[0] != 0)
    {
        esp_mqtt_client_publish(mqtt_client, "/kvas/" ROBOT_NAME "/s_pos", data, 36, 0, 0);
    }
    else
    {
        esp_mqtt_client_publish(mqtt_client, "/kvas/" ROBOT_NAME "/s_ax", data, 36, 0, 0);
    }
}

static void rx_task(void *pvParameter)
{
    static const char *RX_TASK_TAG = "RX_TASK";
    esp_log_level_set(RX_TASK_TAG, ESP_LOG_INFO);
    uint8_t *data = (uint8_t *)malloc(RX_BUF_SIZE + 1);
    ESP_LOGI(RX_TASK_TAG, "Starting RX loop");

    while (1)
    {
        size_t rxBufferLevel;
        uart_get_buffered_data_len(UART_NUM_0, &rxBufferLevel);
        if (rxBufferLevel >= (sizeof(to_mqtt) + 1))
        {
            const int rxBytes = uart_read_bytes(UART_NUM_0, data, sizeof(to_mqtt) + 1, 100 / portTICK_RATE_MS);
            //We add a newline character after the 32 byte data sequence, in case we would like to process it in the interrupt section (however, a byte with value 10 is not unique, maybe combine it with buffer level so it equals out somehow..)
            //if (data[32]==10) {
            //ESP_LOGI(RX_TASK_TAG, "Rec:%d", rxBytes);
            //ESP_LOGI(RX_TASK_TAG, "Data10:%u", data[32]);
            //}

            //We hope (for now), that this synchronises the data flow
            uart_flush_input(UART_NUM_0);
            if (rxBytes > 0)
            {
                char printbuffer[sizeof(to_mqtt) + 1];
                //Just to prevent any string overflows, we cap it after the supposed newline character
                data[sizeof(to_mqtt) + 1] = 0;
                //printf((const char*)data);
                memcpy(&printbuffer, data, sizeof(to_mqtt));
                printbuffer[sizeof(to_mqtt)] = '\n';
                //ESP_LOGI(RX_TASK_TAG, "Received %d bytes: '%s'", rxBytes, printbuffer);
                //ESP_LOGE(RX_TASK_TAG, "Buffer level: %u bytes.", rxBufferLevel);
                //ESP_LOGI(RX_TASK_TAG, "Rec:%d", rxBytes);
                //ESP_LOGE(RX_TASK_TAG, "Buf:%u", rxBufferLevel);
            }
            if (rxBytes == (sizeof(to_mqtt) + 1))
            {
                memcpy(&to_mqtt, data, sizeof(to_mqtt));
                newPosToMQTT = true;
                //data[rxBytes] = 0;
                //
                //ESP_LOG_BUFFER_HEXDUMP(RX_TASK_TAG, data, rxBytes, ESP_LOG_INFO);
            }
        }
        else
        {
            vTaskDelay(10 / portTICK_RATE_MS);
        }
    }
    free(data);
}

static void tx_mqtt(void *pvParameter)

{
    while (1)
    {
        if (newPosToMQTT)
        {
            newPosToMQTT = false;
            auto ptr = &to_mqtt;
            mqtt_sendposition((const char *)ptr);
        }
        vTaskDelay(10 / portTICK_PERIOD_MS);
    }
}

extern "C"
{
    void app_main(void);
}
void app_main()
{
    /* Configure the IOMUX register for pad BLINK_GPIO (some pads are
       muxed to GPIO on reset already, but some default to other
       functions and need to be switched to GPIO. Consult the
       Technical Reference for a list of pads and their default
       functions.)
    */
    ESP_LOGI(TAG, "[APP] Startup..");
    ESP_LOGI(TAG, "[APP] Free memory: %d bytes", esp_get_free_heap_size());
    ESP_LOGI(TAG, "[APP] IDF version: %s", esp_get_idf_version());

    // gpio_pad_select_gpio(BLINK_GPIO);
    /* Set the GPIO as a push/pull output */
    // gpio_set_direction(BLINK_GPIO, GPIO_MODE_OUTPUT);
    ESP_ERROR_CHECK(nvs_flash_init());
    initialise_wifi();
    mqtt_app_start();
    //xTaskCreate(&wpa2_enterprise_example_task, "wpa2_enterprise_example_task", 4096, NULL, 5, NULL);
    uart_init();
    xTaskCreate(rx_task, "uart_rx_task", 1024 * 2, NULL, configMAX_PRIORITIES, NULL);
    xTaskCreate(tx_task, "uart_tx_task", 1024 * 2, NULL, configMAX_PRIORITIES - 1, NULL);
    xTaskCreate(tx_mqtt, "mqtt_tx_task", 1024 * 4, NULL, configMAX_PRIORITIES - 2, NULL);
    esp_log_level_set("*", ESP_LOG_NONE);
}