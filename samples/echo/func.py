import fdk
import ujson


def handler(ctx, data=None, loop=None, **kwargs):
    name = "World"
    if data and len(data) > 0:
        body = ujson.loads(data)
        name = body.get("name")
    return {"message": "Hello {0}".format(name)}


if __name__ == "__main__":
    fdk.handle(handler)
