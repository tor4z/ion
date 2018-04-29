
if __name__ == "__main__":
    client = HTTPClient()
    resp = await client.get("https://www.python.org/")
    print(resp.status_code)