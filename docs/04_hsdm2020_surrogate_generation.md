# Surrogate Generation

Before using the our dataset for the development of de-identification methods, we turned it into a
dummy dataset by replacing protected health information (PHI) with artificial, but realistic
replacements - a process called surrogate generation. We did a (quite ad-hoc) implementation of the
surrogate generation method described by Stubbs et al. (2015). Below, we explain how apply this
method to a new dataset.

## Apply Surrogate Generation Method

### Setup

The surrogate generation scripts use the python `locale` package to support internationalization.
Currently, the script assumes that the `en_US.UTF-8`, `nl_NL.UTF-8` and `de_DE.UTF-8` locales are
installed.

```sh
# Verify that locales are installed
locale -a

# If not, generate the missing locales using the `locales` (e.g., apt-get install locales) package:
sudo dpkg-reconfigure locales
```

### Step 1: Generate surrogates

First, we will generate the surrogates. The command below assumes that your dataset is located in `data/gold-annotations` and is in [standoff format](01_data_format.md).

```sh
python deidentify/surrogates/generate_surrogates.py \
    data/gold-annotations/ \
    data/surrogate-mapping/gold-surrogate-mapping.csv
```

This will output a `.csv` file in following form:

```csv
doc_id,ann_id,text,start,end,tag,surrogate,manual_surrogate,checked
example-1,T1,"van Janssen, Jan",23,39,Name,"Linders, Xandro",,False
example-1,T2,j.van.jansen@nedap.nl,41,62,Email,t.njg.nmmeso@rcrmb.nl,,False
```

### Step 2: Revise automatic replacements

Import the `.csv` file in your favorite spreadsheet editor and fix any automatic replacement errors by adding an entry in the `manual_surrogate` column of the respective row. At the least, the surrogates for the `OTHER` category must be manually added. Afterwards, export the table again to `.csv`.

### Step 3: Rewrite documents/annotation files

Use the following script to replace PHI in the original `*.txt/*.ann` files with the surrogates from the mapping table.

```sh
python deidentify/surrogates/rewrite_dataset.py \
    data/surrogate-mapping/gold-surrogate-mapping-revised.csv \
    data/gold-annotations/ \
    data/surrogate-annotations/
```


## References

* Amber Stubbs, Özlem Uzuner, Christopher Kotfila, Ira Goldstein, and Peter Szolovits. 2015. Challenges in Synthesizing Surrogate PHI in Narrative EMRs. *In Medical Data Privacy Handbook*, Aris Gkoulalas-Divanis and Grigorios Loukides (Eds.). Springer International Publishing, 717–735. DOI: https://doi.org/10.1007/978-3-319-23633-9_27
