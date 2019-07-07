import os
import numpy as np
import stk

if not os.path.exists('building_block_tests_output'):
    os.mkdir('building_block_tests_output')


def test_init(amine2):
    assert len(amine2.func_groups) == 2
    assert amine2.func_groups[0].info.name == 'amine'
    assert len(amine2.atoms) == 15
    assert len(amine2.bonds) == 14


def test_get_bonder_ids(amine2):
    bonder_ids = []
    for func_group in amine2.func_groups:
        for bonder_id in func_group.bonder_ids:
            bonder_ids.append(bonder_id)

    bonder_ids2 = list(amine2.get_bonder_ids())
    assert len(bonder_ids2) == len(bonder_ids)

    s = set(bonder_ids)
    for bonder_id in bonder_ids2:
        assert bonder_id in s


def test_get_bonder_centroids(tmp_aldehyde3):
    coords = np.zeros((len(tmp_aldehyde3.atoms), 3))
    tmp_aldehyde3.set_position_matrix(coords)

    for i, centroid in enumerate(tmp_aldehyde3.get_bonder_centroids()):
        assert len(centroid) == 3
        assert sum(centroid) < 1e-6
    assert i == 2


def test_get_bonder_plane(amine3):
    a, b, c, d = amine3.get_bonder_plane()
    for x, y, z in amine3.get_bonder_centroids():
        product = a*x + b*y + c*z
        assert abs(product-d) < 1e-6


def test_get_bonder_plane_normal(tmp_amine2):
    coords = tmp_amine2.get_position_matrix()
    coords[:, 2] = 0
    tmp_amine2.set_position_matrix(coords)
    assert np.allclose(
        a=tmp_amine2.get_plane_normal(),
        b=[0, 0, 1],
        atol=1e-6
    )


def test_get_bonder_distances(tmp_amine2):
    coords = tmp_amine2.get_position_matrix()
    atoms0 = tmp_amine2.func_groups[0].bonder_ids
    coords[atoms0, :] = np.zeros((len(atoms0), 3))

    atoms1 = tmp_amine2.func_groups[1].bonder_ids
    coords[atoms1, :] = np.zeros((len(atoms1), 3))
    coords[atoms1, 0] = np.ones((len(atoms1, )))

    for fg1, fg2, distance in tmp_amine2.get_bonder_distances():
        assert abs(distance - 1) < 1e-6


def test_get_bonder_direction_vectors(tmp_aldehyde3):
    pos_mat = tmp_aldehyde3.get_position_matrix()
    # Set the coordinate of each bonder to the id of the fg.
    for fg in tmp_aldehyde3.func_groups:
        for bonder in fg.bonder_ids:
            pos_mat[bonder, :] = [fg.id, fg.id, fg.id]
    tmp_aldehyde3.set_position_matrix(pos_mat)

    dir_vectors = tmp_aldehyde3.get_bonder_direction_vectors()
    for i, (id1, id2, v) in enumerate(dir_vectors):
        # Calculate the expected direction vector based on ids.
        d = stk.normalize_vector(np.array([id2]*3) - np.array([id1]*3))
        assert np.allclose(d, v, atol=1e-8)
    assert i == 2


def test_get_centroid_centroid_direction_vector(aldehyde3):
    c1 = aldehyde3.get_centroid(atom_ids=aldehyde3.get_bonder_ids())
    c2 = aldehyde3.get_centroid()
    assert np.allclose(
        a=stk.normalize_vector(c2-c1),
        b=aldehyde3.get_centroid_centroid_direction_vector(),
        atol=1e-8
    )


def test_get_functional_groups(amine2):
    amines = amine2.get_functional_groups(['amine'])

    assert amines[0].atom_ids == (0, 5, 6)
    assert amines[0].bonder_ids == (0, )
    assert amines[0].deleter_ids == (5, 6)

    assert amines[1].atom_ids == (4, 13, 14)
    assert amines[1].bonder_ids == (4, )
    assert amines[1].deleter_ids == (13, 14)

    aldehydes = amine2.get_functional_groups(['aldehyde'])
    assert not aldehydes


def test_dump_and_load(tmp_amine2):
    path = os.path.join('building_block_tests_output', 'mol.dump')

    tmp_amine2.test_attr1 = 'something'
    tmp_amine2.test_attr2 = 12
    tmp_amine2.test_attr3 = ['12', 'something', 21]
    include_attrs = ['test_attr1', 'test_attr2', 'test_attr3']

    tmp_amine2.dump(path, include_attrs)
    mol2 = stk.Molecule.load(path)

    assert tmp_amine2 is not mol2
    assert mol2.func_groups == tmp_amine2.func_groups

    assert tmp_amine2.test_attr1 == mol2.test_attr1
    assert tmp_amine2.test_attr2 == mol2.test_attr2
    assert tmp_amine2.test_attr3 == mol2.test_attr3

    mol3 = stk.Molecule.load(path, use_cache=True)
    assert mol3 is not mol2
    mol4 = stk.Molecule.load(path, use_cache=True)
    assert mol3 is mol4


def test_caching():
    mol0 = stk.BuildingBlock.init_from_smiles('NCCCN', ['amine'])
    mol1 = stk.BuildingBlock.init_from_smiles('NCCCN', ['amine'])
    assert mol0 is not mol1

    mol2 = stk.BuildingBlock.init_from_smiles(
        smiles='NCCCN',
        functional_groups=['amine'],
        use_cache=True
    )
    mol3 = stk.BuildingBlock.init_from_smiles(
        smiles='NCCCN',
        functional_groups=['amine'],
        use_cache=True
    )
    assert mol0 is not mol2 and mol1 is not mol2
    assert mol2 is mol3

    mol4 = stk.BuildingBlock.init_from_smiles(
        smiles='NCCCN',
        functional_groups=['aldehyde'],
        use_cache=True
    )
    assert mol3 is not mol4


def test_shift_fgs(amine4):
    ids = [10, 20, 30, 40]
    shifted = amine4.shift_fgs(ids, 32)

    for i, (fg1, fg2) in enumerate(zip(amine4.func_groups, shifted)):
        assert fg1 is not fg2
        assert fg2.id == ids[i]

        for a1, a2 in zip(fg1.atom_ids, fg2.atom_ids):
            assert a1 + 32 == a2

        for a1, a2 in zip(fg1.bonder_ids, fg2.bonder_ids):
            assert a1 + 32 == a2

        for a1, a2 in zip(fg1.deleter_ids, fg2.deleter_ids):
            assert a1 + 32 == a2
