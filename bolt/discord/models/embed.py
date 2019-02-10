from bolt.discord.models.base import Snowflake, Model, Field, ListField, Enum, Timestamp

class Footer(Model):
    text = Field(str)
    icon_url = Field(str)
    proxy_icon_url = Field(str)

class Image(Model):
    url = Field(str)
    proxy_url = Field(str)
    height = Field(int)
    width = Field(int)

class Thumbnail(Model):
    url = Field(str)
    proxy_url = Field(str)
    height = Field(int)
    width = Field(int)

class Video(Model):
    url = Field(str)
    height = Field(int)
    width = Field(int)

class Provider(Model):
    name = Field(str)
    url = Field(str)

class Author(Model):
    name = Field(str, max_length=256)
    url = Field(str)
    icon_url = Field(str)
    proxy_icon_url = Field(str)

class EmbedField(Model):
    name = Field(str, max_length=25)
    value = Field(str, max_length=1024)
    inline = Field(bool)

class Embed(Model):
    title = Field(str, max_length=256)
    type = Field(str)
    description = Field(str, max_length=2048)
    url = Field(str)
    timestamp = Field(Timestamp)
    color = Field(int)
    footer = Field(Footer)
    image = Field(Image)
    thumbnail = Field(Thumbnail)
    video = Field(Video)
    provider = Field(Provider)
    author = Field(Author)
    fields = ListField(EmbedField, max_length=25)
