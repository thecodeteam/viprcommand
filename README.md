# ViPR Command

ViPR Command provides command line interface for ViPR REST APIs.   

## Introduction
Application that provides unix/linux shell-like command line interface (CLI) for ViPR APIs. It uses WADL & XSD to auto generate the interface. It can be used with any ViPR version. 


## Dependencies  
**ViPR**: 2.2, 2.3  
**Python**: 3.2.5, 3.4 (Additional modules: requests, configparser)  

## Install  

1.	Copy downloaded package to any location  
2.	Windows only: Open cmd prompt  
3.	Navigate to ViPR command downloaded folder  
4.	Navigate to "config" folder and enter your ViPR host in cli_config.ini.  
5.	Navigate to "bin" folder  
6.	Type `python ViPRCommand.py` and press ENTER. The log in prompt appears:  
        login as:  
        Type ViPR username and press ENTER. A password prompt appears:  
        Password:  
        Type password and press ENTER.    
        Instead you could also run 
```
python ViPRCommand.py -username {user} -password {pswd}
```  
 
# Context tree  
  
After logging into ViPR Command it will initially land in root context. From there using "cd" command (explained below) one can navigate to different contexts and sub-contexts. There are 3 components to each context: resources, sub-context and actions.  

_Resources_:  these are ViPR resources in current context, identified by URN. To navigate to resource, use "cd {resource_urn}". 

_Sub-context_: these are children to current context. For example: if you are in "block" context, "exports", "volumes" are some of its sub-contexts. To navigate to sub-context, use `cd {sub_context}`.

_Actions_: List of actions that can be performed on current context. These are commands by themselves.  

Refer to [ViPR REST API](http://www.emc.com/techpubs/api/vipr/v2-3-0-0/index.htm) guide for details on these contexts, actions, payloads etc.  

# Commands  

## Log in/Log out from CLI  
### login  
This command will log user to ViPR.  
  
_Options_  
-username  
-password  

_Example_  

    login -username root -password ChangeMe


### logout
This command will log out user from ViPR  

## Unix-like commands  

### ls  
This command will list all resources in current context  

### ll  
This command will list all resources in current context along with their names  

### cd  
This command will change context. If new context starts with "/" it is treated as absolute path.   

_Arguments_  
{New_context}  

_Examples_  

    cd /block/volumes
    cd projects


###cd ../cd..  
This command will change context to parent (if exists).  

### find  
This command will find all matching context paths for a given resource  

_Arguments_  
{Resource_name}  

_Example_  

    find tenant


### quit  
This command will exit ViPR Command  

## REST operations  

### POST  
This command will create resource in current context. You can write xml or json to file and input that to command or provide them as parameters.  

Building parameters:-  
Parameters are flat view of XML elements. There should be 1 parameter for each required element. All child elements should be typed along with its parents. Ignore XML's root element.  
For example:  
XML  

    <block_export_create>
    	<clusters>
    		<cluster/>
    	</clusters>
    	<hosts>
    		<host/>
    	</hosts>
    	<initiators>
    		<initiator/>
    	</initiators>
    	<name/>
    	<project/>
    	<type/>
    	<varray/>
    	<volumes>
    		<volume>
    			<id/>
    			<lun/>
    		</volume>
    	</volumes>
    </block_export_create>


_Parameters:_  

    -name {name} -project name:{project_name} -type cluster -clusters:cluster {cluster_id} -clusters:cluster {cluster_id} -volumes:volume:id {volume_id} -volumes:volume:lun {volume_lun} -varray name:{varray_name}  


If "MIN" in table is 1, then that element is required. If "MAX" in table is "unbounded", that that element can have multiple values.  

_Arguments_  
help  
json  
xml  

_Examples_  

    POST help  
    POST json payload.json  
    POST xml payload.xml  


Using paramters: create volume example  

    POST -name kbvol -project name:kb -size 1GB -varray name:KB_test_varray -vpool name:KB_json_update


### PUT  
This command will update current resource. This works same as POST.  
_Arguments_  
help  
json  
xml  

_Examples_  

    PUT help  
    PUT json payload.json  
    PUT xml payload.xml   
  

### GET  
This command will return current resource details. By default this command will return data in table format. To format output as xml or json use "accept" option.  

_Arguments_  
help 

_Options_  

    -accept {xml/json}  

_Examples_  

    GET -accept xml
    GET -accept json


### Others  
All "Actions" can be run as commands. Run "help" on them and check if they require any parameters.  

    ViPRCommand:/block/volumes/urn:storageos:Volume:00088e2e-7510-4be7-9a30-75d1bcdc29ab:vdc1/> expand help  
    Payload Fields:-  
    | NAME     | TYPE      | MIN | MAX |  
    | new_size | xs:string | 1   | 1   |  
    
    XML Payload:-  
    <?xml version="1.0" ?>  
    <volume_expand>  
            <new_size/>  
    </volume_expand>


_Examples_  
Expand block volume (Navigate to block volume resource /block/volumes/{id})  

    expand -new_size 10
 

Delete volume (Navigate to block volume resource /block/volumes/{id})  

    deactivate
  

### General rules  
1.	"help" will show input fields in table and xml format  
2.	Before running command, run "ls" to see what actions are supported  
3.	If a field requires URN to be passed you can either send URN or send its name and prefix it with "name".   
For example: to send project as name `-project name:DemoProject`  
4.	Fields can be repeated if they allow multiple values ("MAX" is "unbounded")  
        For example: `-cluster name:clusetr1 -cluster name:cluster2`  

## Searching for a resource  

Search can be performed on resources if it is listed as "sub-context".   
For example: to search for a volume by name  

    cd /block/volumes/search
    GET -name vol1
    
## Deleting a resource  

Resource can be deleted if "deactivate" is found in "actions"  

For example: to delete a block volume  

    cd /block/volumes
    deactivate -id {volume_id}

## Using Query Parameters

Query parameters can be sent in command just like other parameters. To get list of query parameters on a command type "help".

For example: to get a zone details by its name

	ViPRCommand:/vdc/network-systems/urn:storageos:NetworkSystem:8c7be854-2a08-43f9-bb69-966d98ed278f:vdc1/san-fabrics/1/san-zones/>ls  
	Actions:-  
	PUT  POST  activate  remove  GET  

	ViPRCommand:/vdc/network-systems/urn:storageos:NetworkSystem:8c7be854-2a08-43f9-bb69-966d98ed278f:vdc1/san-fabrics/1/san-zones/>GET help  
		Query Parameters:-  
	| Name            | Type       |  
	| exclude-members | xs:boolean |  
	| zone-name       | xs:string  |   

	ViPRCommand:/vdc/network-systems/urn:storageos:NetworkSystem:8c7be854-2a08-43f9-bb69-966d98ed278f:vdc1/san-fabrics/1/san-zones/>GET -zone-name 'SDS_nh1_tz_fc_view_647316423649600_485565236431_0701_FA2F1'  
	| Name      | Value                                                      |  
	| san_zone  |                                                            |  
	|   name    | SDS_nh1_tz_fc_view_647316423649600_485565236431_0701_FA2F1 |  
	|   members |                                                            |  
	|     wwn   | 21:00:48:55:65:23:64:31                                    |  
	|     wwn   | 50:00:09:73:10:0A:F5:45                                    |  

	ViPRCommand:/vdc/network-systems/urn:storageos:NetworkSystem:8c7be854-2a08-43f9-bb69-966d98ed278f:vdc1/san-fabrics/1/san-zones/>GET -zone-name 'SDS_nh1_tz_fc_view_647316423649600_485565236431_0701_FA2F1' -exclude-members True  
	| Name      | Value                                                      |  
	| san_zone  |                                                            |  
	|   name    | SDS_nh1_tz_fc_view_647316423649600_485565236431_0701_FA2F1 |  
	|   members |                                                            |  
