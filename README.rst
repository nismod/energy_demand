.. _readme:

====
High Resolution Energy Demand Model
====

SUBBILBE

Description
===========

LOREM IPSUM
    
HIRE
=======================

**HIRE** is written in Python (Python>=3.5).


Residential model
=======================
NOT IN HEADER BUT NEW TITLE


Data
----

1. Household Electricity Servey <https://www.gov.uk/government/collections/household-electricity-survey> 

    More information:
    Carbon Trust (2007). Advanced metering for SMEs Carbon and cost savings.
    Retrieved from https://www.carbontrust.com/media/77244/ctc713_advanced_metering_for_smes.pdf


2. Household Electricity Servey 

    Minor data cleaning: Removed minus values and filled missing values, removed one or two lines with more values (meausring errors?
    (some entries have huge minus values? Some have more than 48 measurements?, )

    Diff in Electricity demand between Jan and Jul (Jan-Jul) (probably because of lighting and electric space heating/cooling):

                            Overall                 h and max diff (jan-jul)      h and % max diff
                            Jul compared to Jan     Jul compared to Jan           Jul compared to Jan
        Aggregated_rest:    ~                       3,  ~ -23%                    8, +330%
        Community:          ~-7%                    6,  ~ -13%                    -
        Education           ~-30%		    	    10, ~ -36%                    -
        Health              ~-16%                   11, ~ -29%                    - 
        Offices:            ~-2.5% 		            8,  ~ -8%                     19, ~ +3% 
        Retail:             ~-6%                    6, ~ -30%                     21, ~ +12%          

        Whole dataset:      In Jul less demand in early hours (maybe heating?) but more in afternoon (maybe cooling?)



h: 0  %83.9732957283   Diff: -16.0267042717
h: 1  %84.2567692061   Diff: -15.7432307939
h: 2  %82.3492857298   Diff: -17.6507142702
h: 3  %83.4372693692   Diff: -16.5627306308
h: 4  %82.7539800073   Diff: -17.2460199927
h: 5  %82.4058839918   Diff: -17.5941160082
h: 6  %97.8062617142   Diff: -2.1937382858
h: 7  %141.06502334   Diff: +41.06502334
h: 8  %132.023028597   Diff: +32.023028597
h: 9  %114.974726579   Diff: +14.9747265795
h: 10  %147.921724011   Diff: +47.9217240109
h: 11  %138.698853851   Diff: +38.698853851
h: 12  %99.6093262358   Diff: -0.390673764193
h: 13  %150.381949691   Diff: +50.381949691
h: 14  %151.167787197   Diff: +51.1677871974
h: 15  %147.496895086   Diff: +47.4968950856
h: 16  %114.590867414   Diff: +14.590867414
h: 17  %117.022382089   Diff: +17.022382089
h: 18  %120.948872853   Diff: +20.948872853
h: 19  %100.624555256   Diff: +0.624555255971
h: 20  %93.657729214   Diff: -6.34227078605
h: 21  %93.8838966358   Diff: -6.11610336418
h: 22  %91.0740252731   Diff: -8.92597472693
h: 23  %87.2200096511   Diff: -12.7799903489

Description
--------------------

BLABLABLA

    # THIS IS NOW IN A GREY BOX
    LROBEM




A word from our sponsors
========================

**HIRE** was written and developed at the `Environmental Change Institute,
University of Oxford <http://www.eci.ox.ac.uk>`_ within the
EPSRC sponsored MISTRAL programme, as part of the `Infrastructure Transition
Research Consortium <http://www.itrc.org.uk/>`_.
