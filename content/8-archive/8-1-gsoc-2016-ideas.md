---
title: Google Summer of Code 2016 ideas
weight: 1
---

Below are a number of suggestions for students interested in the ModSecurity project during Google Summer of Code. These are just suggestions, feel free to submit your own proposal. If you are looking for more information (or just someone to talk to about ideas) feel free to email security [at] modsecurity.org, join #Modsecurity on freenode, join the mailing lists, or open a github ticket! We look forward to working with you. 
- @csanders-git and @zimmerle

###ModSecurity Ruby support	
**Brief explanation:** Adding the capability of rapid prototyping to ModSecurity functionalities through scripts will open the possibility for easy rules production and customization, It also opens the possibility for a large community such as Ruby developers to create their own customization on the top of ModSecurity and so customize their own rules, analogous of today's Lua support.			
**Expected results:** An implementation able to handle Ruby scripts which will interact to ModSecurity as Lua does.			
**References:**
- Embedding Ruby into C++ (ModSecurity is C, using C++ as reference): http://aeditor.rubyforge.org/ruby_cplusplus/index.html
- ModSecurity Reference Manual, Lua:{{% relref "3-reference-manual/3-2-configuration-directives#secrulescript" %}}"	

###ModSecurity JavaScript support			
**Brief explanation:** Adding the capability of rapid prototyping to ModSecurity functionalities trough scripts will open the possibility for easy rules production and customization, It also opens the possibility for a large community such as JavaScript developers to create their own customization on the top of ModSecurity and so customize their own rules, analogous of today's Lua support.			
**Expected results:** An implementation able to handle JavaScripts scripts which will interact to ModSecurity as Lua does.			
**References:**
- ModSecurity Reference Manual, Lua:{{% relref "3-reference-manual/3-2-configuration-directives#secrulescript" %}}"	

###ModSecurity connector for node.js			
**Brief explanation:** As of ModSecurity version 3, ModSecurity is splited into core and connectors. The connector, as the name suggests, create an interface between the webserver (or other ModSecurity comsumer) to the libModSecurity. By create a connector the target application will be able to apply ModSecurity inspections and actions. The idea of this project is to extend node.js to add ModSecurity support to it.			
Expected results: A connector which will allow ModSecurity to be used inside node.js			
**References:**
- ModSecurity version 3.0:
https://www.trustwave.com/Resources/SpiderLabs-Blog/An-Overview-of-the-Upcoming-libModSecurity/?page=1&year=0&month=0
- ModSecurity nginx connector:
https://github.com/SpiderLabs/ModSecurity-nginx"

###ModSecurity connector for Apache			
**Brief explanation:** As of ModSecurity version 3, ModSecurity is splited into core and connectors. The connector, as the name suggests, create an interface between the webserver (or other ModSecurity comsumer) to the libModSecurity. By create a connector the target application will be able to apply ModSecurity inspections and actions. The idea of this project is to extend Apache to add ModSecurity v3 support to it. Notice: ModSecurity version 2.x is avalable inside Apache, but not v3			
Expected results: A workable but no feature complete connector which will allow ModSecurity v3 to be used inside Apache			
**References:**
- ModSecurity version 3.0:
https://www.trustwave.com/Resources/SpiderLabs-Blog/An-Overview-of-the-Upcoming-libModSecurity/?page=1&year=0&month=0
- ModSecurity nginx connector:
https://github.com/SpiderLabs/ModSecurity-nginx"


###ModSecurity Data persistance layer			
**Brief explanation:** Currently ModSecurity can write audit logs to a file or support logging via a callback function. While this is fantastic if you are building a connector for ModSecurity v3 it doesn't work well if you are an end user. The suggestion is to build a modular system that allows for new persistence layers (mySQL, ElasticSearch, Web Request, File) to be added quickly in  plugin format. The connection details would be supplied by the user via new ModSecurity Directives. This would replace older less extendable methods such as mlogc			
**Expected results:** An implementation that has hooks for various persistence platforms as well as a few example plugins

###ModSecurity Unicode Correctness			
**Brief explanation:** Currently ModSecurity has a number of open issues regarding the parsing of Cyrillic characters. It is unclear if this is a problem with how CRS rules are written or the underlying PCRE engine. This project requires investigating how regular expressions with non-ASCII characters should be handled specifically what the ramifications of switching to the Oniguruma, RE2, or other regex platform.			
**Expected results:** An implementation that can properly handle all unicode characters

###ModSecurityv3 Streaming			
**Brief explanation:** Currently ModSecurity attempts to buffer whole communications before processing them. The current trend within HTTP (HTTP/2) is to use streams for communication. Switching ModSecurity to this model presents some issues but overall will offer better performance and more future proofing			
**Expected results:** An implementation that treats HTTP Requests and Responses and streams instead of buffering them	

###ModSecurityv3 IDS connector			
**Brief explanation:** IDSs like snort support web in a limited way. With the advent of V3 it is possible to put modsecurity into these in a full form. This will allow these other open source projects to leverage a single web parsing framework for better results			
**Expected results:** An implementation of Snort that supports ModSecurity parsing											

###ModSecurity Icap Connector
**Brief explanation:** Adding the capability to connect to a an external malware scanner or content filter via the icap protocol. Antivirus functionality is usually added via the directive @inspectFile, which will then fork a process, or via mod_lua. A proper icap interface would simplify things.
**Expected results:** An interface / directive to interact with a icap enabled scanner / content filter
**References:**
- ICAP (Wikipedia): https://en.wikipedia.org/wiki/Internet_Content_Adaptation_Protocol
- @inspectFile Anti-Virus connector: http://tinyurl.com/hqf9suo

###ModSecurity transformation functions: allow parameters  
**Brief explanation:** Currently, transformations cannot use parameters. This would allow more flexibility.  
**Expected results:** Support parameters  
t:encrypt(%{TX.mykey}%)  


###ModSecurity sub-phases
**Brief explanation:** ModSecurity supports real phases 1-4 and the 'virtual' one 5. Having intermediate virtual phases, like phase:2.2, would allow to order rules inside a real phase. This is especially useful for configurations integrating rules provided, for example, by a hoster and customs ones.   
**Expected results:** Rules will be ordered, inside a phase, not only based on their occurence but also based on their sub-phase.  
**References:** https://github.com/SpiderLabs/ModSecurity/issues/371  
**Example:**  
- SecRule ... phase:2.6,id:1  
- SecRule ... phase:2,id:2  
- SecRule ... phase:2.3,id:3  
Execution order: 2, 3, 1  


###ModSecurity Engine-Mode status
**Brief explanation:** Engine-Mode status is not available for testing nor using (logging in msg, assigning as value).   
**Expected results:** A variable "ENGINE-MODE" could be added.
