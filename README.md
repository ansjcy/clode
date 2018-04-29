# Server Blockchain: 
Cloud, ISP -> post (“/crypto”)   
Params: {  
		cloud_id: string  
		transaction_id: string  
		isp_id: string  
		data: string  
}  
Returns: {  
		result: bool   
}  
  
User-> Post (“/query”)  
Params: {  
		cloud_list: [string]  
}  
Returns: {  
		overlap: double  
}  
  
# Server A B C:   
Blockchain: Post (“/query”)  
Params: {  
	crypto_list: [[string]]  
}  
Returns: {  
	overlap: double  
}  
  
Cloud, ISP -> get(“/public_key”)  
Params: None  
Returns: {  
	public_key: string  
}  
  
# Client cloud: 

# Server ISP: 
blockchain: post("/get_transaction")  
params: {  
	transaction_id: string
}  
returns: {  
	isp_id: string
	data: string
}
# User: 
