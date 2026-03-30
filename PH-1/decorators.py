#logging, cacheing, auth, validation, etc

def logger(func):
    def wrapper(*args):
        print(f"started logging for {func}")
        func(*args)
        print(f"ended logging for{args}")
    return wrapper

@logger
def home_load(name):
    print("Home loaded successfully!")

home_load("Genie")

#stacked decorators, each decorators will wrape the result of previous decorator, from bottom to top

def authentication(func):
    def wrapper(*args):
        print(f"started authentication for {func}")
        func(*args)
        print(f"ended authentication for{args}")
    return wrapper

@logger
@authentication
def home_load_after_auth(name):
    print("Home loaded successfully authenticated!")

# will be like logger(authentication(home_load_after_auth("Genie")))

# output:
# started logging for <function authentication.<locals>.wrapper at 0x000002484F3E9DA0>
# started authentication for <function home_load_after_auth at 0x000002484F3E9D00>
# Home loaded successfully authenticated!
# ended authentication for('Genie',)
# ended logging for('Genie',)

home_load_after_auth("Genie")


#*args -> for non keyworded variable length arguments
#**kwargs -> for keyworded variable length arguments

def add(*args):
    sum = 0
    for i in args:
        sum+=i
    return sum

def print_recrd(**kwargs):
    for k,v in kwargs.items():
        print(f"{k} : {v}")

def discount_price(*args, **kwargs): #always *args first, then **kwargs
    for price in args:
        print(f"Original price: {price}")
        discount = kwargs.get("discount", 1) # get first value, 2nd is default value
        discounted_price = price - (price * discount / 100)
        print(f"Discounted price: {discounted_price}")

add(1,2,3,4,5)
print_recrd(name="Alice", age=30)
discount_price(100, 200, discount=10)