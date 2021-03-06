---


---

<p>This is a crawler which follows ABC algorithm based on URLs IP Address.</p>
<p>Requirement:<br>
Python3.6, Mysql, Beautiful Soup, Gensim.</p>
<p>NOTE:  All files need to be in same folder.</p>
<ul>
<li>
<p>Creating database connections:	<br>
In DSSE_config.ini you will be making changes of the database credentials and database name as well as table name.<br>
As I am using mysql , so my code is based on mysql. You can change it to your confortable database in <a href="http://Crawler.py">Crawler.py</a>, as its following SQLAlchemy.<br>
The schema of the table is DSSE.zip file. You can import that in the database.</p>
</li>
<li>
<p>Change all the file names according to your system.</p>
</li>
<li>
<p>Seed urls can be defined by your own. As I have used Information Security Wiki. But this code is worked for any domain.</p>
</li>
<li>
<p>The key words which I have given in listnames_as_tuple.ini are according to our study and understanding. You can also change according to your understandings.</p>
</li>
<li>
<p>Main file to run is <a href="http://Crawler.py">Crawler.py</a>.</p>
</li>
</ul>
<p>The process of the crawler:</p>
<ul>
<li>It first goes gets PID(Parent ID) from database, and gets into visited list.</li>
<li>It gets request and then fetches plain text from URL, stores in local system and hash value of the plain text is also stored in database as well as local system.</li>
<li>Then it goes finds the similarity score using gensim package.</li>
<li>The similarity is found between the corpus and the sub domain names.</li>
<li>After getting the similarity score that score is stored in the local database usnig csv file.</li>
<li>Then it crawls sub links  and each sub url is checked with visited list whether it is present in it or not.</li>
<li>If url is present in visited list then that url is not considered. The same thing happens while inserting into database.</li>
<li>Each url which is getting inserted into database gets its IP Address and inserts into database.</li>
<li>The next url to be crawled depends by sorting in ascending of sub urls IP ADD.</li>
<li>Those are sorted and are appended into list then those are assigned to thread_initializer where threads are released based on the count of the list.</li>
<li>The process continues…</li>
</ul>

