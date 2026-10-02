# Gerado por tools/export_materials.py. Nao editar manualmente.
PATTERNS = {
    'rolar': r"/rolar\ (?P<dados>(?:[123456789]|1[0123456789]|20)d(?:4|6|8|10|12|20|100)(?:|[\+\-][0123456789](?:|[0123456789])))",
    'atacar': r"/atacar\ (?P<alvo>[abcdefghijklmnopqrstuvwxyz](?:[abcdefghijklmnopqrstuvwxyz0123456789_])*)\ bonus=(?P<bonus>(?:|[\+\-])[0123456789](?:|[0123456789]))\ ca=(?P<ca>[123456789](?:|[0123456789]))\ dano=(?P<dados>(?:[123456789]|1[0123456789]|20)d(?:4|6|8|10|12|20|100)(?:|[\+\-][0123456789](?:|[0123456789])))",
    'magia': r"/magia\ (?P<magia>[abcdefghijklmnopqrstuvwxyz](?:[abcdefghijklmnopqrstuvwxyz0123456789_])*)\ alvo=(?P<alvo>[abcdefghijklmnopqrstuvwxyz](?:[abcdefghijklmnopqrstuvwxyz0123456789_])*)\ cd=(?P<cd>[123456789](?:|[0123456789]))\ bonus=(?P<bonus>(?:|[\+\-])[0123456789](?:|[0123456789]))\ dano=(?P<dados>(?:[123456789]|1[0123456789]|20)d(?:4|6|8|10|12|20|100)(?:|[\+\-][0123456789](?:|[0123456789])))",
    'curar': r"/curar\ (?P<alvo>[abcdefghijklmnopqrstuvwxyz](?:[abcdefghijklmnopqrstuvwxyz0123456789_])*)\ (?P<dados>(?:[123456789]|1[0123456789]|20)d(?:4|6|8|10|12|20|100)(?:|[\+\-][0123456789](?:|[0123456789])))",
    'teste': r"/teste\ (?P<atributo>(?:forca|destreza|constituicao|inteligencia|sabedoria|carisma))\ bonus=(?P<bonus>(?:|[\+\-])[0123456789](?:|[0123456789]))\ cd=(?P<cd>[123456789](?:|[0123456789]))",
}
