import environ
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

def init_env():
    environ.Env.read_env()

def GetEnvObj():
    init_env()
    return env
