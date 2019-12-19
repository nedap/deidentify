def patch_deduce_institutes():
    """Patch the list of deduce institutes with a custom list of institutes.
    This is necessary, as deduce does not provide any other mechanism to configure this list.
    """
    import deduce
    from deduce import utility, lookup_lists
    from os.path import dirname, join
    import shutil

    from importlib import reload

    deduce_instellingen_path = utility.get_data('instellingen.lst')
    shutil.copy(join(dirname(__file__), 'instellingen.lst'), deduce_instellingen_path)

    reload(deduce)
    reload(utility)
    reload(lookup_lists)


if __name__ == '__main__':
    patch_deduce_institutes()
