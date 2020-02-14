#ifndef __EREGEC_PLATFORM_CLIENT_H__
#define __EREGEC_PLATFORM_CLIENT_H__

#include <stdbool.h>

void eregec_init(const char *id, const char *name, const char *host, int port);

bool eregec_connect(void);

bool eregec_connect_command_socket(void);

bool eregec_connect_data_socket(void);

void eregec_disconnect(void);

void eregec_disconnect_command_socket(void);

void eregec_disconnect_data_socket(void);

const char *eregec_get_error_message(void);

bool eregec_is_command_socket_connected(void);

bool eregec_is_connected(void);

void eregec_set_cmd_callback(const char *(*callback_func)(const char *cmd));

void eregec_set_int_data(const char *name, int value);

void eregec_set_float_data(const char *name, float value);

void eregec_set_string_data(const char *name, const char  *value);

bool eregec_upload_data(void);

#endif
