config_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Bolt Config",
    "type": "object",
    "properties": {
        "api_key": {
            "type": "string"
        },
        "name": {
            "type": "string"
        },
        "trigger": {
            "type": "string"
        },
        "worker_threads": {
            "type": "integer"
        },
        "shard_total": {
            "type": "integer"
        },
        "shard_id": {
            "type": "integer"
        },
        "mongo_database_uri": {
            "type": "string",
            "format": "uri"
        },
        "mongo_database_username": {
            "type": "string"
        },
        "mongo_database_password": {
            "type": "string"
        },
        "mongo_database_use_tls": {
            "type": "boolean"
        },
        "webhook_enable": {
            "type": "boolean"
        },
        "webhook_port": {
            "type": "integer",
            "minimum": 0,
            "maximum": 65536
        },
        "backdoor_enable": {
            "type": "boolean"
        },
        "backdoor_host": {
            "type": "string",
            "format": "ipv4"
        },
        "backdoor_port": {
            "type": "integer",
            "minimum": 0,
            "maximum": 65536
        },
        "log_level": {
            "type": "string",
            "enum": [
                "DEBUG",
                "INFO",
                "WARNING",
                "ERROR",
                "CRITICAL"
            ]
        },
        "log_dir": {
            "type": "string"
        },
        "plugins": {
            "type": "object"
        }
    },
    "allOf": [
        {
            "if": {
                "properties": {
                    "webhook_enable": {
                        "const": True
                    }
                }
            },
            "then": {
                "dependencies": {
                    "webhook_enable": {
                        "required": [
                            "webhook_port"
                        ]
                    }
                }
            }
        },
        {
            "if": {
                "properties": {
                    "backdoor_enable": {
                        "const": True
                    }
                }
            },
            "then": {
                "dependencies": {
                    "backdoor_enable": {
                        "required": [
                            "backdoor_host",
                            "backdoor_port"
                        ]
                    }
                }
            }
        }
    ],
    "required": [
        "api_key"
    ]
}
