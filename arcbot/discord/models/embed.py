from arcbot.discord.models.base import *

from datetime import datetime

class Footer(DiscordObject):
    text: str
    icon_url: str
    proxy_icon_url: str

class Image(DiscordObject):
    url: str
    proxy_url: str
    height: int
    width: int

class Thumbnail(DiscordObject):
    url: str
    proxy_url: str
    height: int
    width: int

class Video(DiscordObject):
    url: str
    height: int
    width: int

class Provider(DiscordObject):
    name: str
    url: str

class Author(DiscordObject):
    name: str
    url: str
    icon_url: str
    proxy_icon_url: str

class Field(DiscordObject):
    name: str
    value: str
    inline: bool

class Embed(DiscordObject):
    title: str
    type: str
    description: str
    url: str
    timestamp: datetime
    color: int
    footer: Footer
    image: Image
    thumbnail: Thumbnail
    video: Video
    provider: Provider
    author: Author
    fields: List[Field]
