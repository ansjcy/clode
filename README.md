# Server Blockchain: 
Cloud, ISP -> post (“/crypto”)
Params: {
		type: string (“cloud_crypto”/”isp_crypto”)
cloud_id: string
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

# Client ISP: 

# User: 
