import unittest

import math

from math_prereq import (
    ModInt,
    Pol,
    ModPolGen,
    ModPol,
    Vec,
    Mat,
)


class ModIntTest(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(ModInt(5, 17), ModInt(5, 17))
        self.assertEqual(ModInt(22, 17), ModInt(5, 17))
        self.assertEqual(ModInt(-12, 17), ModInt(5, 17))

        self.assertNotEqual(ModInt(5, 17), ModInt(4, 17))
        self.assertNotEqual(ModInt(5, 17), ModInt(5, 16))

    def test_add(self):
        self.assertEqual(ModInt(9, 17) + ModInt(15, 17), ModInt(7, 17))

    def test_sub(self):
        self.assertEqual(ModInt(9, 17) - ModInt(15, 17), ModInt(11, 17))

    def test_mul(self):
        self.assertEqual(ModInt(9, 17) * ModInt(15, 17), ModInt(16, 17))

    def test_size(self):
        self.assertEqual(ModInt(0, 4).size(), 0)
        self.assertEqual(ModInt(1, 4).size(), 1)
        self.assertEqual(ModInt(2, 4).size(), 2)
        self.assertEqual(ModInt(3, 4).size(), 1)

        self.assertEqual(ModInt(0, 5).size(), 0)
        self.assertEqual(ModInt(1, 5).size(), 1)
        self.assertEqual(ModInt(2, 5).size(), 2)
        self.assertEqual(ModInt(3, 5).size(), 2)
        self.assertEqual(ModInt(4, 5).size(), 1)

    def test_round(self):
        self.assertEqual(ModInt(0, 4).round(), 0)
        self.assertEqual(ModInt(1, 4).round(), 1)
        self.assertEqual(ModInt(2, 4).round(), 1)
        self.assertEqual(ModInt(3, 4).round(), 1)

        # example from slide 47
        self.assertEqual(ModInt(-832, 3329).round(), 0)
        self.assertEqual(ModInt(832, 3329).round(), 0)
        self.assertEqual(ModInt(-833, 3329).round(), 1)
        self.assertEqual(ModInt(833, 3329).round(), 1)

    def test_rand_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        seen0, seen1, seen2 = 0, 0, 0
        times = 30
        for _ in range(times):
            r = ModInt.rand_uni(3)
            if r == ModInt(0, 3):
                seen0 += 1
            if r == ModInt(1, 3):
                seen1 += 1
            if r == ModInt(2, 3):
                seen2 += 1
        self.assertNotEqual(seen0, 0)
        self.assertNotEqual(seen1, 0)
        self.assertNotEqual(seen2, 0)
        self.assertEqual(seen0 + seen1 + seen2, times)

    def test_rand_small_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        seen0, seen1, seen2, seenm1, seenm2 = 0, 0, 0, 0, 0
        times = 50
        q = 3329
        for _ in range(times):
            r = ModInt.rand_small_uni(q, 2)
            if r == ModInt(0, q):
                seen0 += 1
            if r == ModInt(1, q):
                seen1 += 1
            if r == ModInt(2, q):
                seen2 += 1
            if r == ModInt(-1, q):
                seenm1 += 1
            if r == ModInt(-2, q):
                seenm2 += 1
        self.assertNotEqual(seen0, 0)
        self.assertNotEqual(seen1, 0)
        self.assertNotEqual(seen2, 0)
        self.assertNotEqual(seenm1, 0)
        self.assertNotEqual(seenm2, 0)
        self.assertEqual(seen0 + seen1 + seen2 + seenm1 + seenm2, times)


class PolTest(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(
            Pol(7, [1, 2, 3]), Pol(7, [ModInt(1, 7), ModInt(2, 7), ModInt(3, 7)])
        )

        self.assertEqual(Pol(7, [1, 2, 3]), Pol(7, [8, -5, 3]))
        self.assertEqual(Pol(7, [1, 2, 3]), Pol(7, [1, 2, 3, 0, 0]))

        self.assertEqual(Pol(7, [0]), Pol(7, []))

        self.assertNotEqual(Pol(7, [1, 2, 3]), Pol(7, [1, 2, 4]))
        self.assertNotEqual(Pol(7, [1, 2, 3]), Pol(7, [1, 2]))

    def test_add(self):
        # Example from slide 24
        f = Pol(7, [5, 0, 4, 3])
        g = Pol(7, [6, 3, 2])
        s = Pol(7, [4, 3, 6, 3])
        self.assertEqual(f + g, s)
        self.assertEqual(g + f, s)

    def test_sub(self):
        # Example from slide 24
        f = Pol(7, [5, 0, 4, 3])
        g = Pol(7, [6, 3, 2])
        d = Pol(7, [6, 4, 2, 3])
        self.assertEqual(f - g, d)

    def test_mul(self):
        # Example from slide 24
        f = Pol(7, [5, 0, 4, 3])
        g = Pol(7, [6, 3, 2])
        p = Pol(7, [2, 1, 6, 2, 3, 6])
        self.assertEqual(f * g, p)
        self.assertEqual(g * f, p)

    def test_mod(self):
        # Example from slide 26
        h = Pol(41, [24, 19, 16, 24, 26, 25, 22])
        m = Pol(41, [1, 0, 0, 0, 1])
        r = Pol(41, [39, 35, 35, 24])
        self.assertEqual(h % m, r)

    def test_size(self):
        # Example from slide 33
        f = Pol(19, [1, 12, 0, 3, 0, 18])
        self.assertEqual(f.size(), 7)

        # Example from slide 34
        g = Pol(31, [1, 30, 29, 0, 1, 2])
        self.assertEqual(g.size(), 2)


class ModPolGenTest(unittest.TestCase):
    def test_equal(self):
        # Example from slide 26
        h = Pol(41, [24, 19, 16, 24, 26, 25, 22])
        m = Pol(41, [1, 0, 0, 0, 1])
        r = Pol(41, [39, 35, 35, 24])
        self.assertEqual(ModPolGen(h, m), ModPolGen(r, m))

        # wrong leading coefficient
        r2 = Pol(41, [39, 35, 35, 25])
        self.assertNotEqual(ModPolGen(h, m), ModPolGen(r2, m))

    def test_add(self):
        # Example from slide 26
        m = Pol(41, [1, 0, 0, 0, 1])
        f = ModPolGen(Pol(41, [32, 0, 17, 22]), m)
        g = ModPolGen(Pol(41, [11, 7, 19, 1]), m)
        # result computed manually
        s = ModPolGen(Pol(41, [2, 7, 36, 23]), m)
        self.assertEqual(f + g, s)
        self.assertEqual(g + f, s)

    def test_sub(self):
        # Example from slide 26
        m = Pol(41, [1, 0, 0, 0, 1])
        f = ModPolGen(Pol(41, [32, 0, 17, 22]), m)
        g = ModPolGen(Pol(41, [11, 7, 19, 1]), m)
        # results computed manually
        d1 = ModPolGen(Pol(41, [21, 34, 39, 21]), m)
        d2 = ModPolGen(Pol(41, [-21, -34, -39, -21]), m)
        self.assertEqual(f - g, d1)
        self.assertEqual(g - f, d2)

    def test_mul(self):
        # Example from slide 26
        m = Pol(41, [1, 0, 0, 0, 1])
        f = ModPolGen(Pol(41, [32, 0, 17, 22]), m)
        g = ModPolGen(Pol(41, [11, 7, 19, 1]), m)
        r = ModPolGen(Pol(41, [39, 35, 35, 24]), m)
        self.assertEqual(f * g, r)
        self.assertEqual(g * f, r)

    def test_size(self):
        # Examples from slide 35
        m = Pol(41, [1, 0, 0, 0, 1])
        f = ModPolGen(Pol(41, [1, 1, -2, 2]), m)
        g = ModPolGen(Pol(41, [-2, 0, 2, -1]), m)
        self.assertEqual(f.size(), 2)
        self.assertEqual(g.size(), 2)
        self.assertEqual((f * g).size(), 8)


class ModPolTest(unittest.TestCase):
    def test_equal(self):
        r0 = ModPol(41, 4, [39, 35, 35, 24])
        r1 = ModPol(41, 4, [-2, 35, -6, 24])
        self.assertEqual(r0, r1)

        # wrong leading coefficient
        r2 = ModPol(41, 4, [39, 35, 35, 25])
        self.assertNotEqual(r0, r2)

        # wrong integer modulus
        r3 = ModPol(43, 4, [39, 35, 35, 25])
        self.assertNotEqual(r0, r3)

    def test_add(self):
        # Example from slide 26
        f = ModPol(41, 4, [32, 0, 17, 22])
        g = ModPol(41, 4, [11, 7, 19, 1])
        # result computed manually
        s = ModPol(41, 4, [2, 7, 36, 23])
        self.assertEqual(f + g, s)
        self.assertEqual(g + f, s)

    def test_sub(self):
        # Example from slide 26
        f = ModPol(41, 4, [32, 0, 17, 22])
        g = ModPol(41, 4, [11, 7, 19, 1])
        # results computed manually
        d1 = ModPol(41, 4, [21, 34, 39, 21])
        d2 = ModPol(41, 4, [-21, -34, -39, -21])
        self.assertEqual(f - g, d1)
        self.assertEqual(g - f, d2)

    def test_mul(self):
        # Example from slide 26
        f = ModPol(41, 4, [32, 0, 17, 22])
        g = ModPol(41, 4, [11, 7, 19, 1])
        r = ModPol(41, 4, [39, 35, 35, 24])
        self.assertEqual(f * g, r)
        self.assertEqual(g * f, r)

    def test_size(self):
        # Examples from slide 35
        f = ModPol(41, 4, [1, 1, -2, 2])
        g = ModPol(41, 4, [-2, 0, 2, -1])
        self.assertEqual(f.size(), 2)
        self.assertEqual(g.size(), 2)
        self.assertEqual((f * g).size(), 8)

    def test_round(self):
        # Example from slide 47
        f = ModPol(3329, 4, [3000, 1500, 2010, 37])
        g = [0, 1, 1, 0]
        self.assertEqual(f.round(), g)

    def test_rand_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        max_size = 0
        q, n = 17, 8
        for _ in range(100):
            f = ModPol.rand_uni(q, n)
            max_size = max(max_size, f.size())
        self.assertEqual(max_size, q // 2)

        # Ensure we get objects of the right shape
        q, n = 3, 2
        zero = ModPol(q, n, [0, 0])  # proba 1 / 3^2
        seen0 = False
        for _ in range(100):
            seen0 |= ModPol.rand_uni(q, n) == zero
        self.assertTrue(seen0)

    def test_rand_small_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        max_size = 0
        q, n, eta = 3329, 8, 3
        for _ in range(100):
            f = ModPol.rand_small_uni(q, n, eta)
            max_size = max(max_size, f.size())
        self.assertEqual(max_size, eta)

        # Ensure we get objects of the right shape
        q, n, eta = 3329, 2, 1
        zero = ModPol(q, n, [0, 0])  # proba 1 / 3^2
        seen0 = False
        for _ in range(100):
            seen0 |= ModPol.rand_small_uni(q, n, eta) == zero
        self.assertTrue(seen0)

    def test_from_seed(self):
        q, n = 3329, 256

        # https://github.com/C2SP/CCTV/blob/main/ML-KEM/intermediate/ML-KEM-512.txt
        rho = "b1720e4ed5ac0add457f573a041465bcbd7ca4e1d7d53eaadeda511962a36eb0"
        # fmt: off
        exp = [
            2322, 479, 3, 783, 2874, 1746, 2961, 2018, 1000, 667, 1686, 115,
            1257, 268, 1040, 2914, 1051, 1438, 1500, 1887, 2121, 3171, 454,
            2842, 2683, 1412, 2461, 1063, 1892, 2180, 3248, 309, 1300, 776,
            3273, 2631, 445, 2127, 16, 1737, 413, 1477, 834, 1429, 1741, 147,
            1742, 1378, 1295, 2642, 2169, 379, 676, 2115, 1815, 2490, 1119,
            204, 1412, 172, 381, 2697, 1565, 29, 2338, 2357, 3221, 1595, 1597,
            2667, 144, 850, 1017, 986, 2430, 200, 802, 142, 596, 1755, 1439,
            3007, 828, 454, 440, 1161, 1463, 746, 797, 2419, 3124, 992, 2372,
            1092, 889, 2094, 2488, 1185, 630, 1399, 2478, 2984, 482, 2890,
            471, 1276, 1713, 2058, 1890, 1567, 2203, 1421, 2351, 2554, 1681,
            1725, 2133, 1981, 167, 1588, 531, 2889, 90, 2503, 3001, 135, 1878,
            1550, 3185, 1483, 1006, 3242, 2771, 2745, 212, 3307, 1178, 9,
            2523, 373, 2435, 168, 1264, 688, 1091, 1278, 2638, 1319, 380,
            2722, 643, 2199, 653, 1549, 1400, 695, 3187, 1756, 1214, 1235,
            2941, 2467, 1026, 2740, 1758, 511, 2380, 3261, 1177, 2729, 569,
            76, 284, 1958, 1375, 2648, 246, 2220, 2132, 2115, 2202, 908, 2697,
            1437, 647, 1006, 443, 1826, 121, 2597, 835, 432, 213, 1740, 1488,
            899, 3279, 158, 998, 2213, 2724, 2194, 276, 593, 254, 1065, 2437,
            26, 2632, 64, 2763, 1179, 827, 2678, 2272, 575, 2761, 1224, 114,
            2154, 2896, 1511, 2591, 1538, 1452, 3097, 3082, 1448, 1411, 587,
            2265, 3223, 3046, 2500, 2157, 97, 658, 859, 16, 2552, 1376, 2131,
            795, 2368, 2151, 1782, 2712, 1663, 3168, 1803, 1552, 3098, 2249,
            1110, 1645, 1015
        ]
        # fmt: on
        B = bytes.fromhex(rho) + bytes.fromhex("0000")
        gen = ModPol.from_seed(q, n, B)
        self.assertEqual(gen, ModPol(q, n, exp))

        # https://github.com/C2SP/CCTV/blob/main/ML-KEM/intermediate/ML-KEM-768.txt
        rho = "26ffff11b531b1800f4e1fa75c4d008c4f9a112932c669d543551204405da8b4"
        # fmt: off
        exp = [
            1413, 10, 604, 2877, 3203, 1546, 1604, 1174, 616, 1275, 2938, 394,
            1529, 420, 397, 2532, 619, 1129, 2868, 294, 2356, 2288, 1330,
            2649, 2530, 1123, 2119, 3163, 1542, 2725, 1282, 2023, 3308, 1299,
            1987, 2334, 726, 3141, 3114, 1371, 667, 1415, 99, 2891, 2749,
            1816, 584, 2813, 1463, 459, 1848, 185, 1602, 2052, 3209, 3220,
            495, 851, 905, 3314, 2542, 658, 1122, 1500, 663, 1044, 493, 1593,
            1541, 3202, 836, 2236, 281, 829, 2078, 517, 168, 2997, 845, 383,
            432, 2232, 3267, 324, 1024, 1450, 2805, 1484, 1362, 39, 956, 974,
            2289, 1780, 3227, 2180, 619, 1941, 3313, 267, 2992, 1172, 3292,
            2044, 1272, 821, 2785, 697, 2584, 2497, 1377, 3075, 3040, 1149,
            2763, 1577, 142, 1624, 1186, 2703, 166, 1986, 2618, 3051, 1146,
            402, 2003, 1391, 585, 1617, 646, 2176, 3262, 1603, 1543, 2426,
            2188, 1624, 1727, 2735, 335, 2465, 1106, 803, 2364, 500, 31, 219,
            1922, 126, 917, 1821, 3033, 699, 1866, 2205, 1098, 3229, 2689,
            1060, 3256, 1558, 1545, 3206, 678, 672, 1430, 1052, 2905, 3299,
            612, 1960, 2661, 2527, 2546, 2593, 3153, 3168, 922, 2152, 528,
            3076, 746, 3246, 1601, 779, 2135, 2877, 1892, 946, 2771, 354,
            3081, 2793, 3314, 1840, 822, 3124, 2778, 2066, 3188, 2553, 125,
            413, 2694, 2297, 456, 1415, 40, 1073, 51, 476, 1759, 752, 1244,
            3141, 1886, 1189, 1274, 2352, 514, 1853, 2527, 3161, 1094, 3105,
            1794, 1454, 1970, 2704, 2253, 983, 68, 669, 766, 2535, 259, 348,
            2019, 3290, 3261, 1379, 3102, 1277, 401, 110, 2539, 1702, 588,
            2866, 1895, 1203, 1371, 239, 2622, 2237
        ]
        # fmt: on
        B = bytes.fromhex(rho) + bytes.fromhex("0000")
        gen = ModPol.from_seed(q, n, B)
        self.assertEqual(gen, ModPol(q, n, exp))

        # https://github.com/C2SP/CCTV/blob/main/ML-KEM/intermediate/ML-KEM-1024.txt
        rho = "db09edbe4f1a61a62a23531cf707976a861efef13e8347210d77f3d080e9ba89"
        # fmt: off
        exp = [
            1221, 310, 2096, 2198, 2290, 1899, 984, 2261, 2224, 132, 1310,
            3010, 626, 2170, 3038, 836, 2997, 1484, 2674, 2419, 167, 53, 1294,
            484, 1820, 678, 516, 2194, 1984, 638, 1617, 2507, 244, 1692, 1103,
            1238, 3172, 1224, 1328, 1001, 1431, 1347, 2870, 165, 211, 2952,
            203, 196, 2262, 2297, 2150, 2026, 1094, 1608, 1666, 637, 32, 400,
            2399, 2773, 1852, 1148, 403, 1502, 3174, 748, 1627, 1369, 1288,
            587, 545, 2876, 1078, 695, 1306, 2856, 3263, 1791, 679, 3261,
            2418, 3100, 780, 2237, 1530, 1130, 1824, 93, 2046, 1370, 2066,
            1171, 1083, 2623, 2966, 1357, 862, 2079, 3157, 306, 2782, 2476,
            1290, 2828, 2227, 1209, 574, 1731, 1845, 11, 1236, 2741, 1942,
            529, 1537, 2310, 1580, 721, 41, 218, 2644, 2887, 746, 1377, 3212,
            2330, 270, 1674, 1723, 1011, 2229, 1805, 50, 1262, 789, 2105,
            1651, 745, 2043, 2406, 166, 3001, 2603, 2513, 180, 1193, 1254,
            351, 1253, 415, 2768, 2052, 2032, 2846, 1079, 2134, 3197, 151,
            2779, 2863, 2861, 2996, 366, 1254, 2563, 2071, 1839, 406, 1297,
            169, 2349, 3308, 1181, 3019, 1762, 726, 195, 1612, 163, 672, 2583,
            2486, 2285, 124, 1186, 1919, 582, 2462, 1241, 1961, 1711, 3232,
            1851, 2143, 1245, 1524, 3184, 244, 2033, 543, 41, 1808, 1450, 330,
            2609, 3127, 1819, 2811, 2181, 2648, 481, 2542, 3215, 1804, 647,
            2644, 744, 153, 1057, 2641, 2416, 476, 3314, 109, 2411, 1985,
            1311, 2902, 1356, 1392, 2993, 1817, 1747, 1944, 2347, 2438, 1013,
            3167, 2474, 2098, 1752, 621, 1636, 2106, 337, 490, 1195, 3007,
            1021, 1139, 2852, 1822, 208, 971, 525, 643
        ]
        # fmt: on
        B = bytes.fromhex(rho) + bytes.fromhex("0000")
        gen = ModPol.from_seed(q, n, B)
        self.assertEqual(gen, ModPol(q, n, exp))

    @unittest.skip("slow")
    def test_kyber_ring_is_not_an_integral_domain(self):
        # All 3 Kyber/ML-KEM sizes have q = 3329 (a prime number), n = 256.
        # The resulting ring R_q is not an integral domain, that is,
        # we can find non-zero elements whose product is zero.
        #
        # One way to obtain such elements is the factorisation of
        # the modulus X^256 + 1 over GF(3329).
        # All factors happen to be of the form X^2 + c for some constant c.
        # fmt: off
        constants = [
            17, 48, 109, 233, 268, 279, 314, 319,
            375, 394, 403, 525, 540, 554, 556, 561,
            568, 583, 641, 642, 667, 680, 723, 733,
            735, 756, 757, 780, 863, 885, 886, 892,
            939, 941, 952, 992, 1021, 1026, 1029, 1031,
            1041, 1063, 1092, 1100, 1143, 1173, 1175, 1179,
            1212, 1219, 1230, 1239, 1292, 1409, 1455, 1461,
            1482, 1540, 1584, 1607, 1626, 1637, 1645, 1651,
            1678, 1684, 1692, 1703, 1722, 1745, 1789, 1847,
            1868, 1874, 1920, 2037, 2090, 2099, 2110, 2117,
            2150, 2154, 2156, 2186, 2229, 2237, 2266, 2288,
            2298, 2300, 2303, 2308, 2337, 2377, 2388, 2390,
            2437, 2443, 2444, 2466, 2549, 2572, 2573, 2594,
            2596, 2606, 2649, 2662, 2687, 2688, 2746, 2761,
            2768, 2773, 2775, 2789, 2804, 2926, 2935, 2954,
            3010, 3015, 3050, 3061, 3096, 3220, 3281, 3312,
        ]
        # fmt: on
        factors = [ModPol(3329, 256, [c, 0, 1] + [0] * 253) for c in constants]

        zero = ModPol(3329, 256, [0] * 256)
        one = ModPol(3329, 256, [1] + [0] * 255)

        self.assertEqual(math.prod(factors, start=one), zero)


class VecTest(unittest.TestCase):
    # Example from slide 29
    a = Vec(
        ModPol(137, 4, [93, 51, 34, 54]),
        ModPol(137, 4, [27, 87, 81, 6]),
        ModPol(137, 4, [112, 15, 46, 122]),
    )
    b = Vec(
        ModPol(137, 4, [40, 78, 1, 119]),
        ModPol(137, 4, [11, 31, 57, 90]),
        ModPol(137, 4, [108, 72, 47, 14]),
    )
    s = Vec(
        ModPol(137, 4, [133, 129, 35, 36]),
        ModPol(137, 4, [38, 118, 1, 96]),
        ModPol(137, 4, [83, 87, 93, 136]),
    )
    d = Vec(
        ModPol(137, 4, [53, 110, 33, 72]),
        ModPol(137, 4, [16, 56, 24, 53]),
        ModPol(137, 4, [4, 80, 136, 108]),
    )
    p = ModPol(137, 4, [93, 59, 44, 132])

    def test_equal(self):
        self.assertEqual(self.a, self.a)
        self.assertEqual(self.b, self.b)

        self.assertNotEqual(self.a, self.b)
        self.assertNotEqual(self.b, self.a)

    def test_add(self):
        self.assertEqual(self.a + self.b, self.s)
        self.assertEqual(self.b + self.a, self.s)

    def test_sub(self):
        self.assertEqual(self.a - self.b, self.d)

    def test_mul(self):
        self.assertEqual(self.a * self.b, self.p)
        self.assertEqual(self.b * self.a, self.p)

    def test_size(self):
        # ModPol examples from slide 35 - let's create vectors out of them.
        f = ModPol(41, 4, [1, 1, -2, 2])
        g = ModPol(41, 4, [-2, 0, 2, -1])

        self.assertEqual(Vec(f, g).size(), 2)
        self.assertEqual(Vec(g, f).size(), 2)
        self.assertEqual(Vec(f, g, f).size(), 2)
        self.assertEqual(Vec(g, f, g, f).size(), 2)

        self.assertEqual(Vec(f, g, f * g).size(), 8)
        self.assertEqual(Vec(f, f * g, g).size(), 8)
        self.assertEqual(Vec(f * g, f, g).size(), 8)

    def test_rand_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        max_size = 0
        q, n, k = 17, 8, 3
        for _ in range(30):
            v = Vec.rand_uni(q, n, k)
            max_size = max(max_size, v.size())
        self.assertEqual(max_size, q // 2)

        # Ensure we get objects of the right shape
        q, n, k = 3, 2, 1
        zero = Vec(ModPol(q, n, [0, 0]))  # proba 1 / 3^(2*1)
        seen0 = False
        for _ in range(100):
            seen0 |= Vec.rand_uni(q, n, k) == zero
        self.assertTrue(seen0)

    def test_rand_small_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        max_size = 0
        q, n, k, eta = 3329, 8, 2, 3
        for _ in range(50):
            v = Vec.rand_small_uni(q, n, k, eta)
            max_size = max(max_size, v.size())
        self.assertEqual(max_size, eta)

        # Ensure we get objects of the right shape
        q, n, k, eta = 3329, 3, 2, 1
        zeropol = ModPol(q, n, [0, 0, 0])  # 1 / 3^3
        zero = Vec(zeropol, zeropol)  # proba 1 / 3^(3*2) = 1 / 729
        seen0 = False
        for _ in range(10000):
            seen0 |= Vec.rand_small_uni(q, n, k, eta) == zero
        self.assertTrue(seen0)


class MatTest(unittest.TestCase):
    def test_mlwe(self):
        # Example from slide 39
        def P(*c):
            return ModPol(541, 4, c)

        a = Mat(
            Vec(P(442, 502, 513, 15), P(368, 166, 37, 135)),
            Vec(P(479, 532, 116, 41), P(12, 139, 385, 409)),
            Vec(P(29, 394, 503, 389), P(9, 499, 92, 254)),
        )
        s = Vec(P(2, -2, 0, 1), P(3, -2, -2, -2))
        e = Vec(P(2, -2, -1, 0), P(1, 2, 2, 1), P(-2, 0, -1, -2))
        t = Vec(P(30, 252, 401, 332), P(247, 350, 259, 485), P(534, 234, 137, 443))

        self.assertEqual(t, a @ s + e)

        self.assertEqual(s.size(), 3)
        self.assertEqual(e.size(), 2)
        self.assertEqual(t.size(), 259)

    def test_rand_uni(self):
        # Don't actually test the distribution,
        # only the output range.
        max_size = 0
        q, n, k = 17, 8, 3
        for _ in range(10):
            m = Mat.rand_uni(q, n, k)
            sizes = [v.size() for v in m.lines]
            max_size = max(max_size, *sizes)
        self.assertEqual(max_size, q // 2)

        # Ensure we get objects of the right shape
        q, n, k = 3, 2, 1
        zero = Mat(Vec(ModPol(q, n, [0, 0])))  # proba 1 / 3^(2*1)
        seen0 = False
        print(zero)
        for _ in range(100):
            seen0 |= Mat.rand_uni(q, n, k) == zero
            print(Mat.rand_uni(q, n, k))
        self.assertTrue(seen0)

    def test_transpose(self):
        a = ModPol(6, 1, [0])
        b = ModPol(6, 1, [1])
        c = ModPol(6, 1, [2])
        d = ModPol(6, 1, [3])
        e = ModPol(6, 1, [4])
        f = ModPol(6, 1, [5])

        m1 = Mat(Vec(a, b), Vec(c, d))
        m2 = Mat(Vec(a, c), Vec(b, d))
        self.assertEqual(m1.transpose(), m2)
        self.assertEqual(m2.transpose(), m1)

        m1 = Mat(Vec(a, b, c), Vec(d, e, f))
        m2 = Mat(Vec(a, d), Vec(b, e), Vec(c, f))
        self.assertEqual(m1.transpose(), m2)
        self.assertEqual(m2.transpose(), m1)
