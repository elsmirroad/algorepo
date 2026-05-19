from algorepo.config import Config
from algorepo.testers.runners.base import BaseRunner
from algorepo.testers.runners.c import CRunner
from algorepo.testers.runners.cpp import CPPRunner
from algorepo.testers.runners.go import GoRunner
from algorepo.testers.runners.java import JavaRunner
from algorepo.testers.runners.javascript import JavaScriptRunner
from algorepo.testers.runners.kotlin import KotlinRunner
from algorepo.testers.runners.python import PythonRunner
from algorepo.testers.runners.rust import RustRunner
from algorepo.testers.runners.typescript import TypeScriptRunner


def get_runner(language_name: str, config: Config) -> BaseRunner | None:
    if language_name in ("Python", "Python3"):
        return PythonRunner(config)
    elif language_name == "JavaScript":
        return JavaScriptRunner(config)
    elif language_name == "C++":
        return CPPRunner(config)
    elif language_name == "TypeScript":
        return TypeScriptRunner(config)
    elif language_name == "Go":
        return GoRunner(config)
    elif language_name == "Rust":
        return RustRunner(config)
    elif language_name == "C":
        return CRunner(config)
    elif language_name == "Java":
        return JavaRunner(config)
    elif language_name == "Kotlin":
        return KotlinRunner(config)
    return None
