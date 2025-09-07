try:
    from paytmchecksum import PaytmChecksum
    print("PaytmChecksum imported successfully!")
    print(f"PaytmChecksum version: {PaytmChecksum.__version__ if hasattr(PaytmChecksum, '__version__') else '1.7.0'}")
except Exception as e:
    print(f"Error importing PaytmChecksum: {str(e)}")
