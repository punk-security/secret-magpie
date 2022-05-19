class InvalidArgumentsException(Exception):
    def __init__(self, provider, required_args) -> None:
        super().__init__(
            f"The arguments {', '.join(required_args)} are required for {provider}. Use '--help' for more info"
        )
