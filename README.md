# versioned-api

A set of tools and decorators for versioned API development

## Have you met any of the following conditions in your team? If 'yes', versioned-api might be helpful.

#### Before APP v1.0 release

- **Product Manager(PM):** I want an API that returns current time for our iOS & Android APP v1.0.
- **Developer(Dev):** That's easy!
```
# ------------------------------------------------
# REQUEST                                 APP v1.0 
# 
#     http://api.domain.com/current_time/  GET
# ------------------------------------------------
#         ------------------------------------------------
#         RESPONSE
# 
#             {"current_time": "10:35"}
#         ------------------------------------------------
def get(self, request):
    return JSONResponse({"current_time": now.strftime('%H:%M')})
```

#### 2 days later... Planning for APP v1.1

- **PM:** Remember the current_time API? I want to change it to current date&time in IOS 8601.
- **Dev:** OK... I'll do it.
- **PM:** And make sure that don't change anything for APP v1.0!
```
# ------------------------------------------------
# REQUEST                                 APP v1.1 
# 
#     http://api.domain.com/current_time/  GET
# ------------------------------------------------
#         ----------------------------------------------------
#         RESPONSE
# 
#         {"current_time": "2015-05-20T10:35:34.123321+00:00"}
#         ----------------------------------------------------
def get(self, request):
    if get_version(request) == '1.1':
        return JSONResponse({"current_time": now.isoformat()})
    return JSONResponse({"current_time": now.strftime('%H:%M')})
```

#### 30 minutes later... APP v1.1 is released on APP stores

- **PM:** OH MY! The APP online version iOS v1.1 has a BUG! Can you cut the millisecond & timezone part of just for the special version right now?
- **Dev:** What t...
- **PM:** It's urgent!
```
# ------------------------------------------------
# REQUEST                             APP iOS v1.1 
# 
#     http://api.domain.com/current_time/  GET
# ------------------------------------------------
#         ------------------------------------------------
#         RESPONSE
# 
#            {"current_time": "2015-05-20T10:35:34+00:00"}
#         ------------------------------------------------
def get(self, request):
    if get_version(request) == '1.1':
        if get_platform(request) == 'ios':
            return JSONResponse({"current_time": now.strftime('%Y-%m-%dT%H:%M:%S')})
        return JSONResponse({"current_time": now.isoformat()})
    return JSONResponse({"current_time": now.strftime('%H:%M')})
```

#### 1 week later... APP v2.0 is on schedule

- **PM:** Since v2.0 on, there will be lots of changes! I need a all-new API for current time! The response should be...
- **Dev:*** That changes a lot, really!
- **PM:** REMEMBER, v1.x still use this API. Competible with them!
```
# ------------------------------------------------
# REQUEST                             APP v2.0 
# 
#     http://api.domain.com/current_time/  GET
# ------------------------------------------------
#         ------------------------------------------------
#         RESPONSE
# 
#            {
#                 "current_time": {
#                     "year": 2015,
#                     "month": 05,
#                     "day": 20,
#                     "hour": 10,
#                     "minute": 35,
#                     "second": 34
#                 }
#             }
#         ------------------------------------------------
def get(self, request):
    if get_version(request) == '2.0':
        return JSONResponse({"current_time": {
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second,
        }})
    if get_version(request) == '1.1':
        if get_platform(request) == 'ios':
            return JSONResponse({"current_time": now.strftime('%Y-%m-%dT%H:%M:%S')})
        return JSONResponse({"current_time": now.isoformat()})
    return JSONResponse({"current_time": now.strftime('%H:%M')})
```

## Ugly? After using versioned-api, it will be...

```
@va.get
def get_default(self, request):
    return JSONResponse({"current_time": now.strftime('%H:%M')})
    
@va.get('1.1')
def get_1_1(self, request):
    return JSONResponse({"current_time": now.isoformat()})
    
@va.get(ios='1.1', exact=True)
def get_1_1_ios(self, request):
    return JSONResponse({"current_time": now.strftime('%Y-%m-%dT%H:%M:%S')})

@va.get('2.0')
def get_2_0(self, request):
    return JSONResponse({"current_time": {
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
    }})
```

## Version controling is abstracted in another layer, that you don't need to worry about any more. Just

1. Clone and import versioned-api
2. Implement your own Version Class with `__cmp__` method (Here provides a common AppVersion in this repo)
3. Nothing more except having fun with the **decorators**!
