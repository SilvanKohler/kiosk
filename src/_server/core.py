import _server.tables as tables
import uuid
specs = {
    'user': ('usid', ('firstname', 'lastname', 'email', 'avatar')),
    'badge': ('baid', ('badgenumber', 'usid')),
    'product': ('prid', ('name', 'stock', 'price')),
    'purchase': ('puid', ('datetime', 'prid', 'usid', 'amount')),
    'transaction': ('trid', ('datetime', 'usid', 'amount', 'reason'))
}
floats = ['amount', 'price']
ints = ['stock', 'badgenumber']


def get(table, filters):
    content = {'success': False}
    if table in tables.tables.keys():
        parameters = {
            key: (float(value) if key in floats else int(value) if key in ints else value) for
            key, value in filters.items()
        }
        result = tables.get(table)
        for entry in dict(result).items():
            try:
                for parameter in parameters.items():
                    if not ((parameter[0] == specs[table][0] and str(parameter[1]).lower() == str(entry[0]).lower()) or (parameter[0] in specs[table][1] and str(
                            parameter[1]).lower() == str(entry[1][parameter[0]]).lower())):
                        break
                else:
                    content.update({
                        entry[0]: {
                            key: value for key, value in entry[1].items()
                        }
                    })
                    content['success'] = True
            except (KeyError):
                pass
    return content


def create(table, properties):
    content = {'success': False}
    if table in tables.tables.keys():
        parameters = {
            key: (float(value) if key in floats else int(value) if key in ints else value) for
            key, value in properties.items()
        }
        try:
            i = uuid.uuid1().hex
            tables.update(table, {
                i: {
                    spec: parameters[spec] for spec in specs[table][1]
                }
            })
            content[specs[table][0]] = i
            content['success'] = True
        except KeyError:
            pass
    return content


def edit(table, filters, properties=None):
    content = {'success': False}
    if table in tables.tables.keys():
        parameters = {
            key: (float(value) if key in floats else int(value) if key in ints else value) for
            key, value in (filters.items() if properties is None else dict(
                tuple(filters.items()) + tuple(properties.items())).items())
        }
        try:
            pos = tuple(parameters.keys()).index(specs[table][0])
            d = tables.get(table)
            d[parameters[specs[table][0]]].update({
                parameter[0]: parameter[1] for parameter in
                tuple(parameters.items())[:pos] +
                tuple(parameters.items())[pos + 1:]
            })
            tables.update(table, d)
            content['success'] = True
        except KeyError:
            pass
    return content


def delete(table, filters):
    content = {'success': False}
    if table in tables.tables.keys():
        parameters = {
            key: (float(value) if key in floats else int(value) if key in ints else value) for
            key, value in filters.items()
        }
        try:
            tables.delete(table, parameters[specs[table][0]])
            content['success'] = True
        except:
            pass
    return content
