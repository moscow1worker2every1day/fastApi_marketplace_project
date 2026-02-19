#сгенерировать RSA private_key размера 2048
openssl genrsa -out jwt-private.pem 2048

#сгенерировать RSA public_key в паре с private_key размера 1024
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem