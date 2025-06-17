#!/usr/bin/env python3
"""
SSL Certificate Setup Script for Ranch Fire Alert PWA
Creates self-signed certificates for HTTPS development
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta

def install_cryptography():
    """Install cryptography package if not available"""
    try:
        import cryptography
        return True
    except ImportError:
        print("Installing cryptography package...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
            return True
        except subprocess.CalledProcessError:
            return False

def create_openssl_cert():
    """Create certificate using OpenSSL command line"""
    print("Creating certificate with OpenSSL...")
    
    # Create OpenSSL config
    config_content = """
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=US
ST=CA
L=San Francisco
O=Ranch Fire Alert
CN=localhost

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = 127.0.0.1
IP.2 = 0.0.0.0
"""
    
    with open('ssl_config.conf', 'w') as f:
        f.write(config_content)
    
    try:
        # Generate private key
        subprocess.run([
            'openssl', 'genrsa', 
            '-out', 'key.pem', 
            '2048'
        ], check=True, capture_output=True)
        
        # Generate certificate
        subprocess.run([
            'openssl', 'req', 
            '-new', '-x509',
            '-key', 'key.pem',
            '-out', 'cert.pem',
            '-days', '365',
            '-config', 'ssl_config.conf',
            '-extensions', 'v3_req'
        ], check=True, capture_output=True)
        
        # Clean up config file
        os.remove('ssl_config.conf')
        
        print("✅ SSL certificate created successfully with OpenSSL!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ OpenSSL failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ OpenSSL not found. Please install OpenSSL or use Python method.")
        return False

def create_python_cert():
    """Create certificate using Python cryptography library"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import ipaddress
        
        print("Creating certificate with Python cryptography...")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Ranch Fire Alert"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("*.localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                x509.IPAddress(ipaddress.IPv4Address("0.0.0.0")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write certificate and key files
        with open("cert.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open("key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print("✅ SSL certificate created successfully with Python!")
        return True
        
    except ImportError:
        print("❌ cryptography package not available")
        return False
    except Exception as e:
        print(f"❌ Failed to create certificate: {e}")
        return False

def get_local_ip():
    """Get local IP address for mobile testing"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "your-computer-ip"

def main():
    print("🔥 Ranch Fire Alert PWA - SSL Certificate Setup")
    print("=" * 50)
    
    # Check if certificates already exist
    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        print("✅ SSL certificates already exist!")
        response = input("Do you want to recreate them? (y/N): ")
        if response.lower() != 'y':
            print("Using existing certificates.")
            return
    
    print("Creating SSL certificates for HTTPS development...")
    
    # Try different methods
    success = False
    
    # Method 1: Try OpenSSL command line
    if not success:
        success = create_openssl_cert()
    
    # Method 2: Try Python cryptography
    if not success:
        if install_cryptography():
            success = create_python_cert()
    
    if success:
        print("\n🎉 SSL Certificate Setup Complete!")
        print("\n📋 Next Steps:")
        print("1. Run your Flask app: python app.py")
        print("2. Visit: https://localhost:8088")
        local_ip = get_local_ip()
        print(f"3. For mobile testing: https://{local_ip}:8088")
        print("\n⚠️  Browser Security Warning:")
        print("- You'll see a security warning (normal for self-signed certificates)")
        print("- Click 'Advanced' then 'Proceed to localhost' (or similar)")
        print("- On mobile: Tap 'Advanced' then 'Proceed to [IP address]'")
        print("\n🍎 iPhone Testing:")
        print("- Open Safari on iPhone")
        print(f"- Go to https://{local_ip}:8088")
        print("- Accept security warning")
        print("- Test PWA features (add to home screen, notifications)")
        
    else:
        print("\n❌ Failed to create SSL certificates")
        print("\n🔧 Manual Setup Options:")
        print("1. Install OpenSSL and try again")
        print("2. Use mkcert: https://github.com/FiloSottile/mkcert")
        print("3. Use ngrok for external HTTPS: pip install pyngrok")
        print("4. Deploy to a hosting service with built-in SSL")

if __name__ == "__main__":
    main()