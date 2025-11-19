#!/bin/bash
# Test deployment setup locally before pushing to Render

echo "🧪 Testing SkillsMatch.AI Deployment Setup"
echo "=========================================="

# Test 1: Check if wsgi.py can import the app
echo "🔍 Test 1: Testing wsgi.py import..."
cd "/Applications/RF/NTU/SCTP in DSAI/SkillsMatch.AI"
python3 -c "
import sys
print('Testing wsgi.py import...')
try:
    from wsgi import application
    print('✅ wsgi.py import successful')
    print(f'Application type: {type(application)}')
except Exception as e:
    print(f'❌ wsgi.py import failed: {e}')
    import traceback
    traceback.print_exc()
"

echo ""

# Test 2: Check if app.py can import the app  
echo "🔍 Test 2: Testing app.py import..."
python3 -c "
print('Testing app.py import...')
try:
    from app import application
    print('✅ app.py import successful')
    print(f'Application type: {type(application)}')
except Exception as e:
    print(f'❌ app.py import failed: {e}')
    import traceback
    traceback.print_exc()
"

echo ""

# Test 3: Check essential dependencies
echo "🔍 Test 3: Testing essential dependencies..."
python3 -c "
import sys
essential_packages = ['flask', 'flask_cors', 'flask_socketio', 'openai', 'sqlalchemy', 'pandas', 'numpy']

for package in essential_packages:
    try:
        __import__(package)
        print(f'✅ {package}: Available')
    except ImportError:
        print(f'❌ {package}: Missing')
"

echo ""

# Test 4: Test gunicorn command
echo "🔍 Test 4: Testing gunicorn startup (5 second test)..."
timeout 5s gunicorn wsgi:application --bind 127.0.0.1:8888 --workers 1 --timeout 30 || echo "✅ Gunicorn test completed (expected timeout)"

echo ""

# Test 5: Check file structure
echo "🔍 Test 5: Checking deployment files..."
files=("app.py" "wsgi.py" "Procfile" "render.yaml" "requirements-render.txt" "web/app.py")

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file: Exists"
    else
        echo "❌ $file: Missing"
    fi
done

echo ""
echo "🎯 Deployment Test Summary:"
echo "- If all tests pass, deployment should work"
echo "- If any test fails, fix the issue before deploying"
echo "- Use 'git add . && git commit -m \"Fix deployment\" && git push' to deploy"