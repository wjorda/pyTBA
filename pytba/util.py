from typing import List


def team_format(team, format="frc{}"):
    if isinstance(team, int): return format.format(team)
    if isinstance(team, str):
        team = team.lower()
        if team.isdigit(): return team_format(int(team), format)
        if team.startswith("frc"):
            team_int = int(team.replace("frc", ""))
            return team_format(team_int, format)

    raise ValueError("Bad team format: " + str(team))


def flip_alliance(alliance: str) -> str:
    if alliance.lower() == 'blue': return 'red'
    elif alliance.lower() == 'red': return 'blue'
    else: raise ValueError('Invalid alliance color: ' + alliance)


def team_wrap(**kwargs):
    if 'format' not in kwargs:
        format = "frc{}"
    else:
        format = kwargs['format']

    if 'pos' in kwargs.keys() and 'kword' in kwargs.keys():
        raise ValueError('Using both pos and kword arguments is not currently supported. Use stacked decorators instead.')

    if 'pos' in kwargs.keys():
        pos = kwargs['pos']
        if not isinstance(pos, (list, tuple)): pos = [pos]

        def decorator(func):
            def wrapped(*args, **kwargs):
                newargs = list(args)
                for i in pos:
                    team = args[i]
                    team = team_format(team, format)
                    newargs[i] = team
                return func(*newargs, **kwargs)

            return wrapped

        return decorator
    elif 'kword' in kwargs.keys():
        kword = kwargs['kword']
        if not isinstance(kword, (list, tuple)): kword = [kword]

        def decorator(func):
            def wrapped(*args, **kwargs):
                for kw in kword:
                    if kw not in kwargs: continue
                    team = kwargs[kw]
                    team = team_format(team, format)
                    kwargs[kw] = team
                return func(*args, **kwargs)

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
        if str(key).isdigit(): key = int(key)
        object = object[key]

    return object


def match_stat(match, alliance, key):
    path = 'score_breakdown/' + alliance + '/' + key
    import dpath
    return dpath.util.get(match, path)


def list2dict(lst: List, keysource='index'):
    if keysource == 'index':
        return dict((i, lst[i]) for i in range(len(lst)))
    elif isinstance(keysource, str):
        import dpath
        return dict((dpath.util.get(item, keysource), item) for item in lst)
    elif isinstance(keysource, list):
        return dict((keysource[i], lst[i]) for i in range(len(lst)))
    elif callable(keysource):
        return dict((keysource(item), item) for item in lst)
