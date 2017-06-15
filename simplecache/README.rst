   simplecache 是一个基于redis(以及内置dict)的简单缓存库，通过装饰器修饰需要缓存的方法以及函数
  一.install:
     git clone git@github.com:cszixin/cached.git &&
     cd cache/simplecache && sudo python setup.py install
  二. code:: python

    import time
    import simplecache

    @simplecache.simplecache(cache_key='result', max_age=5)  # max_age key在缓存中的过期时间，默认100s
    def execute_expensive():
        print 'original function called'
        time.sleep(15)
        return 42

    print execute_expensive()  # 等待15s后执行 ...
    original function called
    42
    print execute_expensive()  # ...结果已经缓存，不用等待15s，直接从redis中获取 ...
    42
    print simplecache.default_backend.get('result') # ..从缓存中获取result的值
    42
    time.sleep(5)              # 等待过期...
    execute_expensive()        # 又需要等待15s ...
    original function called
    42
    print execute_expensive()  # ...重新又缓存 ...
    42
    print simplecache.get_default_backend().data   # get all k:v from cache 


或许你想根据函数的参数来生成cache_key,看下面
the function:

.. code:: python


    @simplecache(cache_key='sum_of_{0}_and_{1}')   # 根据函数的第一，第二参数生成cache_key
    def cached_sum(x, y):                        
        return x + y

    print cached_sum(28, 14)
    42
    print simplecache.default_backend.get('sum_of_28_and_14')
    42

You can also create the key based on **partial arguments** or on the
``attributes``/``items`` within the arguments.

.. code:: python


    class User:
        def __init__(self, name, session_key):
            self.name = name
            self.session_key = session_key

    @simplecache(cache_key='{user_obj.name}')   # 依赖参数的name属性
    def get_username(user_obj):               
        time.sleep(15)
        return user_obj.name

    a = User(name='steve', session_key='0123456789')
    b = User(name='steve', session_key='9876543210') # same name, different session

    print get_username(user_obj=a)   # 等待15s执行 ...
    steve
    print get_username(user_obj=a)   # ...不用等待'...
    steve
    print get_username(user_obj=b)   # ...仍然不用等待 !
    steve


    @simplecache(cache_key='{choices[0]}_{menu[lunch]}')         # build the cache
    def supersized_lunch(ignored, choices=None, menu=None):    # key dependent on
        time.sleep(15)                                         # partial arguments
        return 'You get a %s %s' % (choices[-1], menu['lunch'])

    menu = {'breakfast' : 'eggs',
            'lunch'     : 'pizza',
            'dinner'    : 'steak'}

    sizes = ['small', 'medium', 'large', 'supersize']

    print supersized_lunch('ignored', choices=sizes, menu=menu)
    You get a supersize pizza       # This will take 15 seconds to execute ...

    print supersized_lunch('changed', choices=sizes, menu=menu)
    You get a supersize pizza       # ...not this tho'...

If that format specification for the ``cache_key`` looks familiar,
you've discovered the *secret* of simplecache !

.. code:: python
redis_bacend = RedisCache(master,salve)  # 设置redis为缓存，master为主服务器，salve为从服务器，参数形式'127.0.0.1:6379'
simplecache.set_default_backend(redis_bacend)   # 设置redis为默认缓存


    @simplecache(backend=redis_backend, cache_key='{0}_{kw[foo]}_{obj.x}')
    def custom_key_built_from_args(positional, kw=None, obj=None):
        # now, simplecache will build the `cache_key` from the arguments passed and
        # use the memcached_backend instance to `set` the key with the return value
        # of this function
        return 'cached'

cache_key/expire_key的秘密在于使用了format()函数

cache_key/expire_key 还支持函数
.. code:: python

    def extract_path(url=None, *args, **kwags):
        return urlparse.urlparse(url).path

    @simplecache(cache_key=extract_path, ignore_errors=False)
    def do_something_with(url):
    # 将extract_path的返回值，作为cache_key
        return 'cached'

    do_something_with('http://www.example.com/foo/bar')
    'cached'
    simplecache.default_backend.get('/foo/bar')
    'cached'

当然你也可以实现自己的backend,只要继承BaseCache类，并至少实现get,set,delete,clear四个方法

