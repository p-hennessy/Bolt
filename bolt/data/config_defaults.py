config_defaults = {
    "name": "Bolt",
    "trigger": ".",
    "worker_threads": 1,
    "shard_total": 1,
    "shard_id": 0,
    "mongo_database_uri": "mongodb://localhost:27017",
    "mongo_database_username": "",
    "mongo_database_password": "",
    "mongo_database_use_tls": False,
    "webhook_enable": False,
    "backdoor_enable": False,
    "log_level": "INFO",
    "log_dir": "/var/log/bolt/",
    "plugins": {}
}
