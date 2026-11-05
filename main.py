

import shlex

from mini_redis import MiniRedis


def execute_command(redis, command_line):
    """사용자 명령어를 해석하고 실행한다."""

    try:
        parts = shlex.split(command_line)
    except ValueError:
        return "(error) ERR invalid quotes"

    if not parts:
        return None

    cmd = parts[0].upper()
    args = parts[1:]

    # SET
    if cmd == "SET":
        if len(args) != 2:
            return "(error) ERR wrong number of arguments for 'SET' command"
        return redis.set(args[0], args[1])

    # GET
    if cmd == "GET":
        if len(args) != 1:
            return "(error) ERR wrong number of arguments for 'GET' command"
        return redis.get(args[0])

    # DEL
    if cmd == "DEL":
        if len(args) != 1:
            return "(error) ERR wrong number of arguments for 'DEL' command"
        return redis.delete(args[0])

    # EXISTS
    if cmd == "EXISTS":
        if len(args) != 1:
            return "(error) ERR wrong number of arguments for 'EXISTS' command"
        return redis.exists(args[0])

    # DBSIZE
    if cmd == "DBSIZE":
        if len(args) != 0:
            return "(error) ERR wrong number of arguments for 'DBSIZE' command"
        return redis.dbsize()

    # KEYS
    if cmd == "KEYS":
        if len(args) != 0:
            return "(error) ERR wrong number of arguments for 'KEYS' command"
        return redis.keys()

    # EXPIRE
    if cmd == "EXPIRE":
        if len(args) != 2:
            return "(error) ERR wrong number of arguments for 'EXPIRE' command"

        try:
            seconds = int(args[1])
        except ValueError:
            return "(error) ERR value is not an integer or out of range"

        return redis.expire(args[0], seconds)

    # TTL
    if cmd == "TTL":
        if len(args) != 1:
            return "(error) ERR wrong number of arguments for 'TTL' command"
        return redis.ttl(args[0])

    # CONFIG SET maxmemory
    if cmd == "CONFIG":
        if (
            len(args) != 3
            or args[0].upper() != "SET"
            or args[1].lower() != "maxmemory"
        ):
            return "(error) ERR wrong number of arguments for 'CONFIG' command"

        try:
            memory_limit = int(args[2])
        except ValueError:
            return "(error) ERR value is not an integer or out of range"

        return redis.config_set_maxmemory(memory_limit)

    # INFO memory
    if cmd == "INFO":
        if len(args) != 1 or args[0].lower() != "memory":
            return "(error) ERR wrong number of arguments for 'INFO' command"

        return redis.info_memory()

    return f"(error) ERR unknown command '{cmd}'"


def main():
    """Mini Redis CLI 실행"""

    redis = MiniRedis()

    print("Mini Redis 실행!")
    print("종료하려면 exit 또는 quit 입력")

    while True:
        try:
            command_line = input("mini-redis> ")

        except (EOFError, KeyboardInterrupt):
            print("\nMini Redis 종료")
            break

        if command_line.strip().lower() in ("exit", "quit"):
            print("Mini Redis 종료")
            break

        result = execute_command(redis, command_line)

        if result is not None:
            print(result)


if __name__ == "__main__":
    main()
