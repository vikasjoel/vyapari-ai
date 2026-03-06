#!/bin/bash

# Vyapari.ai — Production Deployment Test Script
# Tests CloudFront frontend and API backend

echo "🧪 Vyapari.ai Deployment Test"
echo "=============================="
echo ""

CLOUDFRONT_URL="${CLOUDFRONT_URL:-https://YOUR_CLOUDFRONT_DOMAIN}"
API_URL="${API_URL:-http://localhost:8000}"

PASSED=0
FAILED=0

pass() {
    echo "✓ PASS: $1"
    PASSED=$((PASSED + 1))
}

fail() {
    echo "✗ FAIL: $1"
    FAILED=$((FAILED + 1))
}

echo "📦 Frontend Tests (CloudFront + S3)"
echo "-----------------------------------"

# Test 1: Homepage loads
if curl -s -f -o /dev/null "$CLOUDFRONT_URL/" 2>/dev/null; then
    pass "Homepage loads (HTTP 200)"
else
    fail "Homepage loads (HTTP 200)"
fi

# Test 2: Correct title
if curl -s "$CLOUDFRONT_URL/" 2>/dev/null | grep -q "Vyapari.ai"; then
    pass "Page title contains 'Vyapari.ai'"
else
    fail "Page title contains 'Vyapari.ai'"
fi

# Test 3: Main JS bundle
JS_FILE=$(curl -s "$CLOUDFRONT_URL/" 2>/dev/null | grep -o 'src="/assets/index-[^"]*\.js"' | sed 's/src="//;s/"$//')
if [ -n "$JS_FILE" ] && curl -s -f -o /dev/null "$CLOUDFRONT_URL$JS_FILE" 2>/dev/null; then
    pass "Main JS bundle loads"
else
    fail "Main JS bundle loads"
fi

# Test 4: CSS file
CSS_FILE=$(curl -s "$CLOUDFRONT_URL/" 2>/dev/null | grep -o 'href="/assets/index-[^"]*\.css"' | sed 's/href="//;s/"$//')
if [ -n "$CSS_FILE" ] && curl -s -f -o /dev/null "$CLOUDFRONT_URL$CSS_FILE" 2>/dev/null; then
    pass "CSS file loads"
else
    fail "CSS file loads"
fi

# Test 5: Google Fonts
if curl -s "$CLOUDFRONT_URL/" 2>/dev/null | grep -q "fonts.googleapis.com"; then
    pass "Google Fonts configured"
else
    fail "Google Fonts configured"
fi

echo ""
echo "🔌 Backend API Tests (localhost:8000)"
echo "-------------------------------------"

# Test 6: Health check
if curl -s "$API_URL/api/health" 2>/dev/null | grep -q '"status":"ok"'; then
    pass "API health check returns 'ok'"
else
    fail "API health check returns 'ok'"
fi

# Test 7: Demo merchants endpoint
if curl -s "$API_URL/api/demo/merchants" 2>/dev/null | grep -q '"merchants"'; then
    pass "Demo merchants endpoint works"
else
    fail "Demo merchants endpoint works"
fi

# Test 8: Template endpoint
if curl -s "$API_URL/api/template/kirana" 2>/dev/null | grep -q '"categories"'; then
    pass "Template endpoint returns categories"
else
    fail "Template endpoint returns categories"
fi

# Test 9: CORS headers
if curl -s -I -H "Origin: $CLOUDFRONT_URL" "$API_URL/api/health" 2>/dev/null | grep -qi "access-control-allow-origin"; then
    pass "CORS headers present"
else
    fail "CORS headers present"
fi

echo ""
echo "🔍 Infrastructure Tests"
echo "----------------------"

# Test 10: S3 bucket
S3_WEB="${S3_WEB_BUCKET:-vyapari-web}"
if aws s3 ls "s3://$S3_WEB/" >/dev/null 2>&1; then
    pass "S3 bucket accessible"
else
    fail "S3 bucket accessible"
fi

# Test 11: CloudFront distribution
CF_DIST_ID="${CLOUDFRONT_DISTRIBUTION_ID:-YOUR_DISTRIBUTION_ID}"
if aws cloudfront get-distribution --id "$CF_DIST_ID" >/dev/null 2>&1; then
    pass "CloudFront distribution exists"
else
    fail "CloudFront distribution exists"
fi

# Test 12: DynamoDB tables
if aws dynamodb describe-table --table-name vyapari-merchants >/dev/null 2>&1; then
    pass "DynamoDB tables accessible"
else
    fail "DynamoDB tables accessible"
fi

echo ""
echo "📊 Test Summary"
echo "==============="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All tests passed! Deployment is ready."
    exit 0
else
    echo "⚠️  Some tests failed. Please review."
    exit 1
fi
