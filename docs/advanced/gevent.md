# Gevent

## Overview

Bolt uses Gevent to allow for highly concurrent functioning.

At a high level, Bolt creates threads for everything it does. There will be green threads for:

* Websocket Listener
* Webhook HTTP Server
* Scheduler
* Workers

## Blocking

{% hint style="warning" %}
It is important to remember to NEVER calling a function that [blocks IO](https://stackoverflow.com/questions/15680422/difference-between-wait-and-blocked-thread-states).
{% endhint %}

Gevent will patch parts of the standard library on functions that would normally block IO, however it's still possible to block by using `time.sleep()`. If you need to introduce a delay, use [`gevent.sleep()`](http://www.gevent.org/api/gevent.html#sleeping) instead.

Gevent does _NOT_ patch file IO. Usually this is already so fast there's not a lot of benefit to it. This is part of the reason Bolt uses MongoDB for it's database, since that will be handled via a socket.

