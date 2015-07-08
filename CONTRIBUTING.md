Setting up a developer workstation
==================================

This will document the installation steps to get the miseq pipeline running locally on your workstation.
The steps are for Eclipse with PyDev on Ubuntu, adapt as needed to your preferred IDE or operating system.

Java and Python
---------------
1. Check that you are running a 64-bit operating system, or bowtie2 won't work.
   Check About this Computer under the gear menu.
2. If you want to edit Python code using PyDev and Eclipse, you will need to
   install Java. Check the version of Java you have installed:

        java -version
 
3. If the java version is lower than 1.7, then install JDK7:

        sudo apt-get install openjdk-7-source

4. Check that you are now using the new version. If not, configure it.

        java -version
        sudo update-alternatives --config java 
        java -version

5. Check the version of Python you have installed:

        python --version

6. If the Python version is lower than 2.7, then install it:
        
        sudo apt-get install python2.7
        
7. Install [pip the Python package manager][pip] and a couple of packages for Python:

        sudo apt-get install python-pip
        sudo pip install testfixtures
        sudo pip install requests

[pip]: https://pip.pypa.io/en/latest/installing.html

Eclipse
-------
1. Install Eclipse, although you might prefer a more recent version from the [Eclipse web site][eclipse]:

        sudo apt-get install eclipse

2. Launch Eclipse. From the Help menu, choose either Eclipse Marketplace... or Install New Software....
3. In the marketplace, just type PyDev and search. In the install wizard, use the [PyDev update site][pydev].
4. After installing PyDev, open Window: Preferences. Navigate down to PyDev: Interpreters: Python Interpreter. 
5. Click the Quick Auto-Config button. Click OK.
6. From the File menu, choose Import.... Navigate down to Git: Projects from Git.
7. Choose Clone URI, and paste this URI: https://github.com/ArtPoon/MiseqPipeline.git
8. Take all the branches, and select dev as your initial branch.
9. Select import existing projects, and finish the import.

[eclipse]: https://www.eclipse.org/downloads/
[pydev]: http://pydev.org/updates

Bowtie, Samtools, and Hyphy
---------------------------
1. Download the latest version of [bowtie2's binaries for Linux][bowtie2].
2. Right click and choose Extract Here. Change the folder owner to root, move it to /opt, and add it to the path.

        chmod g-w -R bowtie2-2.2.1
        sudo chown root:root -R bowtie2-2.2.1
        sudo mv bowtie2-2.2.1 /opt
        sudo vi /etc/environment # add :/opt/bowtie2-2.2.1 and logout/login
        bowtie2 --version # smoke test

3. Before you can build samtools, you will need these libraries:

        sudo apt-get install zlib1g-dev libncurses5-dev

4. Download the latest version of the [source for samtools][samtools].
5. Extract the files, and follow the instructions in the INSTALL file. Copy the samtools executable to /usr/bin.
6. Before you can build HyPhy, you will need these libraries:

        sudo apt-get install build-essential python-dev libcurl4-openssl-dev libcrypto++-dev libssl-dev

7. Download the latest [source for HyPhy][hyphy]. Right click the zip file and choose Expand Here. Then run the setup script:

        cd ~/Downloads/hyphy-master/src/lib
        sudo python setup.py install

    You can test it out if you like.

        cd Examples/Python
        python BasicHyPhy.py # Just check that there are no obvious errors.

[bowtie2]: http://sourceforge.net/projects/bowtie-bio/files/bowtie2/
[samtools]: http://sourceforge.net/projects/samtools/files/
[hyphy]: https://github.com/veg/hyphy

Alignment library
-----------------
MiCall uses an implementation of a modified Gotoh algorithm for pairwise sequence alignment.
This is written in the C++ source file `alignment.cpp`.  To compile this into a shared library
that can be accessed from Python, go to `micall/alignment` and enter the following:
```
sudo python setup.py install
```
This assumes that you have superuser permissions on your system.  We have tested this
installation on OS-X and Ubuntu.


MPI
---
1. Install Open MPI.

    sudo apt-get install openmpi-bin
    
2. Install mpi4py.

    sudo apt-get install python-mpi4py

Running the code
----------------
1. Copy settings_default.py to settings.py, and open it for editing.
2. Set `base_path` to '../', and comment out the next line with the
   production/development extensions.
3. Change `counting_processes` to match the number of processors on your
   computer, and set `mapping_processes` to be that number divided by four.
4. If you want to reduce the combinations that run, remove all but the first 
    value in g2p_fpr_cutoffs, v3_mincounts, conseq_mixture_cutoffs. Remove all 
    but 15 from sam2csf_q_cutoffs.
5. Copy hostfile_default to hostfile, and open it for editing.
6. You probably just want to uncomment the localhost line.
7. Try the launch configurations. They are saved in the `working` directory,
    but you should see them if you open the Run menu and choose Run
    configurations.... If you want to run all steps at once, skip to the next
    step, otherwise go through the numbered launch configurations in order.
8. Copy all the files from the microtest folder to the working folder.
9. Run the sample_pipeline or run_processor launch configurations. They will
    process all the sample files in the working folder. 
12. Run the unit tests. Either run them from Eclipse, or run them from the
    command line like this:

        cd ~/git/MiseqPipeline
        python -m unittest discover -p '*_test.py'
        ruby -rubygems -I"lib:test" *_test.rb
    
Test data
---------
If you want to run MISEQ_MONITOR.py, you have to set up data folders for raw
data and for the working folders.

1. Create a data folder somewhere on your workstation, like ~/data. Create
   subdirectories called miseq and RAW_DATA. Add folders RAW_DATA/MiSeq/runs.
2. Connect to the shared drive [using CIFS][cifs] and mount 
   smb://192.168.68.144/RAW_DATA as /media/RAW_DATA.
3. Navigate down to /media/RAW_DATA/MiSeq/runs, pick a recent folder, and make
   sure it has a file named needsprocessing.
4. Copy SampleSheet.csv to a sample run folder under your local
   RAW_DATA/MiSeq/runs folder.
5. Navigate down to Data\Intensities\BaseCalls, and copy a few of the .fastq.gz
   files to your sample run folder.
6. Open settings.py for editing.
7. Point `home` at your local data/miseq folder.
8. Point `rawdata_mount` at your local RAW_DATA folder.
9. Set the Oracle connection information to a test database where you can upload
   sequence data.
10. Run MISEQ_MONITOR.py, it doesn't take any arguments.

[cifs]: https://wiki.ubuntu.com/MountWindowsSharesPermanently

Looking at SAM files
--------------------
When you don't understand the pipeline's output, it can be helpful to look at
the raw reads in a sequence viewer like [Tablet][tablet]. Change the settings
file on your workstation to not delete the temp folders, then run the pipeline
on a run with a single sample. Look through the temp folders to find the one
for the step you're interested in. For the remap step, the final remap results
are stored in a SAM file named for the seed region. You also have to edit the
`cfe.fasta` file and rename that seed region to "0", because the SAM file uses
the region name "0" instead of the proper region name. Once you've done that,
you should be able to open an assembly in Tablet using the SAM file and the
edited FASTA file.

[tablet]: http://ics.hutton.ac.uk/tablet/

Releases
--------
This section assumes you already have a working server up and running, and you
just want to publish a new release. If you're setting up a new server, follow
similar steps to setting up a development workstation. Follow these steps:

1. Make sure the code works in your development environment. Run all the unit
    tests as described above, process the microtest data set, and process a full
    run using MISEQ_MONITOR.py from the command line. Check the logs for errors.
    Also check that all the issues in the current milestone are closed.
2. Determine what version number should be used next. Update the version number
    in `settings_default.py` if it hasn't been updated already, commit, and push.
3. [Create a release][release] on Github. Use "vX.Y" as the tag, where X.Y
    matches the version you used in `settings_default.py`. If you have to redo
    a release, you can create additional releases with tags vX.Y.1, vX.Y.2, and
    so on. Mark the release as pre-release until you finish deploying it.
4. Get the code from Github into the server's development environment.

    ```
    ssh user@server
    cd /usr/local/share/miseq/development/
    git fetch github
    git checkout tags/vX.Y
    ```

5. Check if you need to set any new settings by running
    `diff settings_default.py settings.py`. You will probably need to modify
    the version number, at least. Make sure that `production = False`, and the
    process counts are half the production values. Do the same comparison of
    `hostfile`.
6. Process one full run of data.

    ```
    cd /usr/local/share/miseq/development/
    ./run_processor.py /data/miseq/YYMMDD*
    ```

7. Stop the `MISEQ_MONITOR.py` process after you check that it's not processing
    any runs.

    ```
    ssh user@server
    tail /data/miseq/MISEQ_MONITOR_OUTPUT.log
    ps aux|grep MISEQ_MONITOR.py
    sudo kill -9 <process id from grep output>
    ```

8. Get the code from Github into the server's production environment.

    ```
    ssh user@server
    cd /usr/local/share/miseq/production/
    git fetch
    git checkout tags/vX.Y
    ```
        
9. Review the settings and host file just as you did in the development
    environment, but make sure that `production = True`.
10. Start the monitor, and tail the log to see that it begins processing all the
    runs with the new version of the pipeline.

    ```
    cd /usr/local/share/miseq/production/
    python MISEQ_MONITOR.py &>/dev/null &
    tail -f /data/miseq/MISEQ_MONITOR_OUTPUT.log
    ```
    
11. Remove the pre-release flag from the release.
12. Send an e-mail to users describing the major changes in the release.
13. Close the milestone for this release, create one for the next release, and
    decide which issues you will include in that milestone.

[release]: https://help.github.com/categories/85/articles
