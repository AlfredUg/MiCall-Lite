import unittest
import StringIO
import project_config

class ProjectConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.defaultJsonIO = StringIO.StringIO("""\
{
  "projects": {
    "R1": {
      "max_variants": 5,
      "regions": [
        {
          "coordinate_region": "R1",
          "seed_region": "R1-seed",
          "id": 10042
        }
      ]
    }
  },
  "regions": {
    "R1-seed": {
      "is_nucleotide": true,
      "reference": [
        "ACTGAAA",
        "GGG"
      ]
    },
    "R1": {
      "is_nucleotide": false,
      "reference": [
        "RWN",
        "NWR"
      ]
    }
  }
}
""")
        self.config = project_config.ProjectConfig()
        
    def testConvert(self):
        expected_fasta = """\
>R1-seed
ACTGAAAGGG
"""
        fasta = StringIO.StringIO()

        self.config.load(self.defaultJsonIO)
        self.config.writeSeedFasta(fasta)
        
        self.assertMultiLineEqual(expected_fasta, fasta.getvalue())

    def testSharedRegions(self):
        jsonIO = StringIO.StringIO("""\
{
  "projects": {
    "R1": {
      "regions": [
        {
          "coordinate_region": null,
          "seed_region": "R1-seed"
        }
      ]
    },
    "R1 and R2": {
      "regions": [
        {
          "coordinate_region": null,
          "seed_region": "R1-seed"
        },
        {
          "coordinate_region": null,
          "seed_region": "R2-seed"
        }
      ]
    }
  },
  "regions": {
    "R1-seed": {
      "is_nucleotide": true,
      "reference": [
        "ACTGAAA",
        "GGG"
      ]
    },
    "R2-seed": {
      "is_nucleotide": true,
      "reference": [
        "TTT"
      ]
    }
  }
}
""")
        expected_fasta = """\
>R1-seed
ACTGAAAGGG
>R2-seed
TTT
"""
        fasta = StringIO.StringIO()

        self.config.load(jsonIO)
        self.config.writeSeedFasta(fasta)
        
        self.assertMultiLineEqual(expected_fasta, fasta.getvalue())

    def testUnusedRegion(self):
        jsonIO = StringIO.StringIO("""\
{
  "projects": {
    "R1": {
      "regions": [
        {
          "coordinate_region": null,
          "seed_region": "R1-seed"
        }
      ]
    }
  },
  "regions": {
    "R1-seed": {
      "is_nucleotide": true,
      "reference": [
        "ACTGAAA",
        "GGG"
      ]
    },
    "R2-seed": {
      "is_nucleotide": true,
      "reference": [
        "TTT"
      ]
    }
  }
}
""")
        expected_fasta = """\
>R1-seed
ACTGAAAGGG
"""
        fasta = StringIO.StringIO()

        self.config.load(jsonIO)
        self.config.writeSeedFasta(fasta)
        
        self.assertMultiLineEqual(expected_fasta, fasta.getvalue())

    def testGetReference(self):
        self.config.load(self.defaultJsonIO)
        seed_name = 'R1-seed'
        expected_ref = 'ACTGAAAGGG'
        
        seed_ref = self.config.getReference(seed_name)
        
        self.assertSequenceEqual(expected_ref, seed_ref)

    def testGetCoordinateReferences(self):
        self.config.load(self.defaultJsonIO)
        seed_name = 'R1-seed'
        expected_refs = {'R1': 'RWNNWR'}
        
        coordinate_refs = self.config.getCoordinateReferences(seed_name)
        
        self.assertDictEqual(expected_refs, coordinate_refs)

    def testUnknownReference(self):
        self.config.load(self.defaultJsonIO)
        seed_name = 'R-unknown'
        
        self.assertRaises(KeyError, self.config.getReference, seed_name)

    def testMaxVariants(self):
        self.config.load(self.defaultJsonIO)
        coordinate_region_name = 'R1'
        
        self.assertEqual(5, self.config.getMaxVariants(coordinate_region_name))

    def testMaxVariantsUnusedRegion(self):
        jsonIO = StringIO.StringIO("""\
{
  "projects": {
    "R1": {
      "max_variants": 2,
      "regions": [
        {
          "coordinate_region": "R1",
          "seed_region": "R1-seed"
        }
      ]
    }
  },
  "regions": {
    "R1-seed": {
      "is_nucleotide": true,
      "reference": [
        "ACTGAAA",
        "GGG"
      ]
    },
    "R1": {
      "is_nucleotide": false,
      "reference": [
        "NSFW"
      ]
    },
    "R2": {
      "is_nucleotide": false,
      "reference": [
        "RSW"
      ]
    }
  }
}
""")
        self.config.load(jsonIO)
        coordinate_region_name = 'R2'
        
        self.assertEqual(0, self.config.getMaxVariants(coordinate_region_name))

    def testMaxVariantsTwoProjects(self):
        """ If two projects specify a maximum for the same coordinate region,
        use the bigger of the two.
        """
        jsonIO = StringIO.StringIO("""\
{
  "projects": {
    "R1": {
      "max_variants": 9,
      "regions": [
        {
          "coordinate_region": "R1",
          "seed_region": "R1-seed"
        }
      ]
    },
    "R1-and-R2": {
      "max_variants": 2,
      "regions": [
        {
          "coordinate_region": "R1",
          "seed_region": "R1-seed"
        },
        {
          "coordinate_region": "R2",
          "seed_region": "R1-seed"
        }
      ]
    }
  },
  "regions": {
    "R1-seed": {
      "is_nucleotide": true,
      "reference": [
        "ACTGAAA",
        "GGG"
      ]
    },
    "R1": {
      "is_nucleotide": false,
      "reference": [
        "NSFW"
      ]
    },
    "R2": {
      "is_nucleotide": false,
      "reference": [
        "RSW"
      ]
    }
  }
}
""")
        self.config.load(jsonIO)
        coordinate_region_name = 'R1'
        
        self.assertEqual(9, self.config.getMaxVariants(coordinate_region_name))
        
    def testReload(self):
        jsonIO1 = StringIO.StringIO("""\
{
  "projects": {
    "R1": {
      "regions": [
        {
          "coordinate_region": null,
          "seed_region": "R1-seed"
        }
      ]
    }
  },
  "regions": {
    "R1-seed": {
      "is_nucleotide": true,
      "reference": [
        "ACTGAAA",
        "GGG"
      ]
    }
  }
}
""")
        jsonIO2 = StringIO.StringIO("""\
{
  "projects": {
    "R2": {
      "regions": [
        {
          "coordinate_region": null,
          "seed_region": "R2-seed"
        }
      ]
    }
  },
  "regions": {
    "R2-seed": {
      "is_nucleotide": true,
      "reference": [
        "GACCTA"
      ]
    }
  }
}
""")
         
        self.config.load(jsonIO1)
        self.config.load(jsonIO2)
        
        self.assertRaises(KeyError, self.config.getReference, "R1-seed")
        self.assertSequenceEqual("GACCTA", self.config.getReference("R2-seed"))

    def testProjectSeeds(self):
        expected_seeds = set(['R1-seed'])
        
        self.config.load(self.defaultJsonIO)
        seeds = self.config.getProjectSeeds('R1')
        
        self.assertSetEqual(expected_seeds, seeds)

    def testFindProjectRegion(self):
        expected_project_region_id = 10042
        expected_seed = 'R1-seed'
        self.config.load(self.defaultJsonIO)
        
        project_region_id, seed = self.config.findProjectRegion(
            project_name="R1",
            coordinate_region_name="R1")
        
        self.assertEqual(expected_project_region_id, project_region_id)
        self.assertEqual(expected_seed, seed)

    def testFindProjectRegionUnknownRegion(self):
        self.config.load(self.defaultJsonIO)
        
        self.assertRaisesRegexp(
            KeyError,
            "Coordinate region 'RXXX' not found in project 'R1'",
            self.config.findProjectRegion,
            project_name='R1',
            coordinate_region_name='RXXX')

    def testFindProjectRegionUnknownProject(self):
        self.config.load(self.defaultJsonIO)
        
        self.assertRaisesRegexp(
            KeyError,
            "Project 'RXXX' not found",
            self.config.findProjectRegion,
            project_name='RXXX',
            coordinate_region_name='R1')
        