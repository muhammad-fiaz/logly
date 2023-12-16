import logly



logly.info("Hello World!", "info", color=logly.COLOR.CYAN)
logly.warn("Hello World!", "warn", color=logly.COLOR.YELLOW)
logly.error("Hello World!", "error", color=logly.COLOR.RED)
logly.debug("Hello World!", "debug", color=logly.COLOR.BLUE)
logly.critical("Hello World!", "critical", color=logly.COLOR.CRITICAL)
logly.fatal("Hello World!", "fatal", color=logly.COLOR.CRITICAL)
logly.trace("Hello World!", "trace", color=logly.COLOR.BLUE)
logly.log("Hello World!", "log", color=logly.COLOR.WHITE)



logly.info("Another Message", "info")
logly.warn("Another Message", "warn")
logly.error("Another Message", "error")
logly.debug("Another Message", "debug")
logly.critical("Another Message", "critical")
logly.fatal("Another Message", "fatal")
logly.trace("Another Message", "trace")
logly.log("Another Message", "log")
