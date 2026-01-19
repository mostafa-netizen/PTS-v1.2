"""
Test script to verify the setup and dependencies.
"""

import sys
import importlib

def test_imports():
    """Test if all required modules can be imported."""
    print("=" * 60)
    print("🧪 Testing Module Imports")
    print("=" * 60)
    
    modules = [
        ('numpy', 'NumPy'),
        ('cv2', 'OpenCV'),
        ('pandas', 'Pandas'),
        ('pdf2image', 'PDF2Image'),
        ('torch', 'PyTorch'),
        ('tqdm', 'TQDM'),
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('doctr', 'DocTR'),
    ]
    
    optional_modules = [
        ('redis', 'Redis'),
        ('rq', 'RQ'),
        ('boto3', 'Boto3'),
        ('openpyxl', 'OpenPyXL'),
    ]
    
    success = True
    
    # Test required modules
    print("\n📦 Required Modules:")
    for module_name, display_name in modules:
        try:
            mod = importlib.import_module(module_name)
            version = getattr(mod, '__version__', 'unknown')
            print(f"  ✅ {display_name:20} {version}")
        except ImportError as e:
            print(f"  ❌ {display_name:20} NOT FOUND")
            success = False
    
    # Test optional modules
    print("\n📦 Optional Modules (for production):")
    for module_name, display_name in optional_modules:
        try:
            mod = importlib.import_module(module_name)
            version = getattr(mod, '__version__', 'unknown')
            print(f"  ✅ {display_name:20} {version}")
        except ImportError:
            print(f"  ⚠️  {display_name:20} Not installed (optional)")
    
    return success


def test_gpu():
    """Test GPU availability."""
    print("\n" + "=" * 60)
    print("🎮 Testing GPU Availability")
    print("=" * 60)
    
    try:
        import torch
        
        if torch.cuda.is_available():
            print(f"  ✅ CUDA available")
            print(f"     Device: {torch.cuda.get_device_name(0)}")
            print(f"     CUDA Version: {torch.version.cuda}")
        elif torch.backends.mps.is_available():
            print(f"  ✅ MPS (Apple Silicon) available")
            print(f"     Device: Apple Silicon GPU")
        else:
            print(f"  ⚠️  No GPU available, will use CPU")
            print(f"     This is fine for testing but slower for production")
        
        return True
    except Exception as e:
        print(f"  ❌ Error checking GPU: {e}")
        return False


def test_config():
    """Test configuration."""
    print("\n" + "=" * 60)
    print("⚙️  Testing Configuration")
    print("=" * 60)
    
    try:
        import config
        
        print(f"  ✅ Config loaded successfully")
        print(f"     PDF DPI: {config.PDF_DPI}")
        print(f"     OCR Batch Size: {config.OCR_BATCH_SIZE}")
        print(f"     Server Port: {config.SERVER_PORT}")
        print(f"     Use GPU: {config.USE_GPU}")
        print(f"     Output Folder: {config.OUTPUT_FOLDER}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error loading config: {e}")
        return False


def test_services():
    """Test service imports."""
    print("\n" + "=" * 60)
    print("🔧 Testing Services")
    print("=" * 60)
    
    try:
        from services.processing_service import ProcessingService
        from services.storage_service import StorageService
        from services.job_queue import get_job_queue
        
        print(f"  ✅ ProcessingService imported")
        print(f"  ✅ StorageService imported")
        print(f"  ✅ JobQueue imported")
        
        # Test instantiation
        storage = StorageService()
        print(f"  ✅ StorageService instantiated")
        
        processing = ProcessingService(storage_service=storage)
        print(f"  ✅ ProcessingService instantiated")
        
        job_queue = get_job_queue()
        print(f"  ✅ JobQueue instantiated")
        
        return True
    except Exception as e:
        print(f"  ❌ Error testing services: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api():
    """Test API imports."""
    print("\n" + "=" * 60)
    print("🌐 Testing API")
    print("=" * 60)
    
    try:
        from api import api_bp
        from api.upload import upload_bp
        from api.processing import processing_bp
        from api.results import results_bp
        
        print(f"  ✅ API blueprints imported")
        print(f"     - Upload API")
        print(f"     - Processing API")
        print(f"     - Results API")
        
        return True
    except Exception as e:
        print(f"  ❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🚀 TENDON ANALYSIS PLATFORM - SETUP TEST")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("GPU", test_gpu()))
    results.append(("Config", test_config()))
    results.append(("Services", test_services()))
    results.append(("API", test_api()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All tests passed! System is ready.")
        print("\nNext steps:")
        print("  1. Run: python app_new.py")
        print("  2. Open: http://localhost:3000")
        print("  3. Upload a PDF file to test")
        return 0
    else:
        print("\n❌ Some tests failed. Please install missing dependencies:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == '__main__':
    sys.exit(main())

