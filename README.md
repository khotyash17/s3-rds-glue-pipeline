# 🚀 S3 to RDS with AWS Glue Fallback – Dockerized Python App
### This project is a Dockerized Python application that:
- 📥 Reads CSV files from an **Amazon S3 bucket**
- 🗄️ Uploads the data to a **MySQL-compatible RDS database**
- 🔁 Falls back to **AWS Glue Data Catalog** if RDS is unavailable

## 📦 Features
- ✅ Automates data ingestion from S3
- ✅ Uses Secrets Manager to fetch RDS credentials
- ✅ Falls back to Glue by creating an external table pointing to S3
- ✅ Dockerized for easy deployment

## 🛠️ Tech Stack
- **Python 3.9-slim**
- **AWS S3, RDS, Glue, Secrets Manager**
- **Docker**
- Libraries: `boto3`, `pandas`, `sqlalchemy`, `pymysql`

## 🧪 Sample CSV File
```
sample.csv
```
## 🧾 Environment Variables (.env file)
### Create .env file
```
S3_BUCKET=my-bucket
CSV_KEY=datasets/sample.csv
RDS_TABLE=users
GLUE_DB=myglue
GLUE_TABLE=users_glue
GLUE_LOCATION=s3://my-bucket/datasets/
SECRET_NAME=rds/mysql/prod

```
## Set Up S3 Bucket
- Create Folder ``` datasets ```
- ``` datasets ``` **Upload file** ``` sample.csv ``` file

## Create RDS MySQL Instance
1. Open RDS Console → Launch DB → MySQL
2. Choose Free Tier
3. DB Name: mydb, Username: admin, Password: YourStrongPassword
4. Enable Public Access and whitelist your IP in the VPC Security Group
5. Save:
  - Hostname (e.g., mydb.xxxxx.us-east-1.rds.amazonaws.com)
  - Port (3306)
  - DB name, username, password

##  Store Credentials in AWS Secrets Manager
Go to AWS → Secrets Manager > Store new secret:
  - Secret type: Other
  - Key/Value:
```
{
  "username": "admin",
  "password": "YourStrongPassword",
  "host": "mydb.xxxxxx.rds.amazonaws.com",
  "db": "mydb"
}
```
- Secret name: rds/mysql/prod
- 
## Launch EC2 Instance 
  - Launch Server
  - Amazon Linux 2
1. Login to server using ssh
2. Clone this repository
   - ``` git clone https://github.com/khotyash17/s3-rds-glue-pipeline.git ``` 
4. Set Up Docker
   - Install Docker ``` sudo yum install docker -y ```
   - Start Docker ``` sudo systemctl docker start ```
   - Enable Docker  ```sudo systemctl enable docker ```

##  Build and Run the Container
``` sudo docker build -t s3-rds-glue . ```

## Run Docker Container 
```  sudo docker run --env-file .env \
  -e AWS_ACCESS_KEY_ID=Your Access Key \
  -e AWS_SECRET_ACCESS_KEY=Your Secret Key \
  -e AWS_DEFAULT_REGION=your region \
  s3-eds-glue
```
## Fallback Logic
### If the RDS upload fails (e.g., DB down), the app:
  - Creates a Glue database and table
  - Registers the CSV file location in S3
  - Columns default to string type for flexibility

## 📂 Project Structure
```
.
├── main.py             # Main Python script
├── Dockerfile          # Docker instructions
├── requirements.txt    # Python packages
├── .env.example        # Sample environment file
├── sample.csv          # Sample CSV to upload
├── README.md           # This file
└── .gitignore          # Excludes sensitive files
```
**## ✍️ Author
Made with 💡 to demonstrate AWS data pipelines and fault tolerance using Python & Docker.**
