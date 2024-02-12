terraform {
  backend "s3" {
    bucket  = "euw1-bluetab-general-tfstate-pro"
    key     = "anime-recommender.tfstate"
    region  = "eu-west-1"
    profile = "practica-cloud"
  }
}
