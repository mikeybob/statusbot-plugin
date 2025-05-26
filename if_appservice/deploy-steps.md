
### **Deployment Steps**


**Generate Appservice Token**
 
   ```bash
   openssl rand -hex 32 > as_token.txt
   ```

**Register Appservice**
  
   ```bash
   sudo cp registration.yaml /etc/matrix-synapse/
   sudo systemctl restart matrix-synapse
   ```

**Build & Deploy**
 
   ```bash
   mbc build
   mbc push -b http://your-maubot-server:29316
   ```

**Verify Permissions**
 
   ```bash
   curl -X PUT \
     -H "Authorization: Bearer $(cat as_token.txt)" \
     -d '{"presence":"online","status_msg":"TEST"}' \
     "https://matrix.yourdomain.com/_matrix/client/v3/presence/@youruser:yourdomain.com/status"
   ```
