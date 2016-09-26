def team_format(team, format="frc{}"):
    if isinstance(team, int): return format.format(team)
    if isinstance(team, str):
        team = team.lower()
        if team.isdigit(): return team_format(int(team), format)
        if team.startswith("frc"):
            team_int = int(team.replace("frc", ""))
            return team_format(team_int, format)

    raise ValueError("Bad team format: " + str(team))


def team_wrap(**kwargs):
    if 'format' not in kwargs:
        format = "frc{}"
    else:
        format = kwargs['format']

    if 'pos' in kwargs.keys():
        pos = kwargs['pos']

        def decorator(func):
            def wrapped(*args):
                team = args[pos]
                team = team_format(team, format)
                newargs = list(args)
                newargs[pos] = team
                return func(*newargs)

            return wrapped

        return decorator
    elif 'kword' in kwargs.keys():
        kword = kwargs['kword']

        def decorator(func):
            def wrapped(**kwargs):
                team = kwargs[kword]
                team = team_format(team, format)
                kwargs[kword] = team
                return func(**kwargs)

            return wrapped

        return decorator
    else:
        pos = 0

        def decorator(func):
            def wrapped(*args):
                team = args[pos]
                team = team_format(team, format)

                newargs = list(args)
                newargs[pos] = team
                return func(*newargs)

            return wrapped

        return decorator


def follow_dict_path(object: dict, path: str, sep: str = '/'):
    keynames = path.split(sep)
    for key in keynames:
        if len(str(key)) == 0: continue
        object = object[key]

    return object


def match_stat(match, alliance, key):
    path = 'score_breakdown/' + alliance + '/' + key
    import dpath
    return dpath.util.get(match, path)