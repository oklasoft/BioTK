===================
Expression analysis
===================

BioTK aims to provide an alternative to the standard R/Bioconductor
environment to perform run-of-the-mill differential expression analyses. Thus,
BioTK has the ability to perform all the standard steps in a differential
expression analysis pipeline:

1. Loading raw or preprocessed data
2. Preprocessing and normalizing the data
3. Finding differentially expressed probes/genes between conditions
4. Analyses of DE gene lists:
   - Performing enrichment analyses against ontologies
   - Visualizing expression or DE results as heatmaps or networks

There are also features for downstream analyses of and methods to take large
collections of expression data, from GEO, in-house data, or a combination
thereof, and use these collections for large-scale meta-analysis.

.. todo::
    - put a simple example of a complete-ish analysis here
    - possibly explain important data structures?

Loading expression data
=======================

From Affymetrix CEL files
-------------------------

From GEO
--------

From RNA-seq aligned reads
--------------------------

Normalizing expression data
===========================

Quantile normalization
----------------------

Differential expression
=======================

Currently, the available differential expression algorithms are:

- t-test
- ANOVA
- SAM  
  
In the future, we plan to provide either a port or a simplified Python
interface to the R package limma, which is one of the most popular tools for
finding DE genes.

T-test
------

ANOVA
-----

SAM
---

Visualization
=============

Heatmap
-------

Enrichment analysis
===================

Meta-analysis
=============

BioTK can store large amounts of expression data from multiple experiments and
even multiple organisms and efficiently perform meta-analyses on this data.
Please see :ref:`meta_analysis`.
