
### **Deployment Steps**


**Generate Appservice Token**
 
   ```bash
   openssl rand -hex 32 > as_token.txt
   cp as_token /mike/home/synapse-env-py310/
   ```

**Register Appservice**
  
   ```bash
   sudo cp registration.yaml /etc/matrix-synapse/
   sudo systemctl restart matrix-synapse
   ```
   
   >**demonlab.net is synctl.**<br>  
   >**Do this instead:**
   
   ```bash
   sudo cp registration.yaml /mike/home/synapse-env-py310/
   synctl restart 
   ```
   

**Build & Deploy**
 
   ```bash
   mbc build
   mbc push -b http://your-maubot-server:29316 #validate this command. Not in docs.
   ```

**Verify Permissions**
 
   ```bash
   curl -X PUT \
     -H "Authorization: Bearer $(cat as_token.txt)" \
     -d '{"presence":"online","status_msg":"TEST"}' \
     "https://matrix.yourdomain.com/_matrix/client/v3/presence/@youruser:yourdomain.com/status"
   ```
