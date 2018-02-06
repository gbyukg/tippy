class MetaSingleton(type):
    # 类属性，用来保存实例对象
    # 设置为类私有属性，防止被意外修改
    __instance = None

    def __call__(cls, *args, **kvargs):
        # 如果类属性 __instance 不为空，说明已经实例化过某个类，直接返回那个类实例即可
        # 如果为 None，则创建一个新的实例对象，并保存到 __instance 变量中
        if cls.__instance is None:
            cls.__instance = super(MetaSingleton, cls).__call__(*args, **kvargs)

        # 总是返回类属性 __instance
        return cls.__instance

class MetaSingleton2(type):
    def __call__(cls, *args, **kvargs):
        return super(MetaSingleton2, cls).__call__(*args, **kvargs)

class Animal(metaclass=MetaSingleton): pass
class Dog(Animal, metaclass=MetaSingleton2): pass

dog1 = Dog()
dog2 = Dog()
print(id(dog1))
print(id(dog2))