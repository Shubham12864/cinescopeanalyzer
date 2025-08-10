const fs = require('fs');
const path = require('path');

function checkNodeVersion() {
    const version = process.version;
    const majorVersion = parseInt(version.slice(1).split('.')[0]);
    console.log(`Node.js version: ${version}`);
    
    if (majorVersion >= 18) {
        console.log('✅ Node.js version is compatible');
        return true;
    } else {
        console.log('❌ Node.js version should be 18+');
        return false;
    }
}

function checkDependencies() {
    const packageJsonPath = path.join(__dirname, 'package.json');
    const nodeModulesPath = path.join(__dirname, 'node_modules');
    
    if (!fs.existsSync(packageJsonPath)) {
        console.log('❌ package.json not found');
        return false;
    }
    
    if (!fs.existsSync(nodeModulesPath)) {
        console.log('❌ node_modules not found - run npm install');
        return false;
    }
    
    console.log('✅ Dependencies folder exists');
    return true;
}

function checkProjectStructure() {
    const requiredFiles = [
        'app/layout.tsx',
        'app/page.tsx',
        'app/globals.css',
        'lib/api.ts',
        'contexts/movie-context.tsx'
    ];
    
    console.log('📁 Checking project structure...');
    let allExist = true;
    
    for (const file of requiredFiles) {
        const filePath = path.join(__dirname, file);
        if (fs.existsSync(filePath)) {
            console.log(`✅ ${file}`);
        } else {
            console.log(`❌ ${file} missing`);
            allExist = false;
        }
    }
    
    return allExist;
}

function checkNextConfig() {
    const nextConfigPath = path.join(__dirname, 'next.config.mjs');
    if (fs.existsSync(nextConfigPath)) {
        console.log('✅ next.config.mjs exists');
        return true;
    } else {
        console.log('❌ next.config.mjs missing');
        return false;
    }
}

function main() {
    console.log('🔍 CineScope Analyzer Frontend Diagnostic');
    console.log('='.repeat(50));
    
    const checks = [
        ['Node.js Version', checkNodeVersion],
        ['Dependencies', checkDependencies],
        ['Project Structure', checkProjectStructure],
        ['Next.js Config', checkNextConfig]
    ];
    
    const results = [];
    for (const [name, checkFunc] of checks) {
        console.log(`\n📋 Checking ${name}...`);
        const result = checkFunc();
        results.push([name, result]);
    }
    
    console.log('\n' + '='.repeat(50));
    console.log('🎯 DIAGNOSTIC SUMMARY:');
    let allPassed = true;
    
    for (const [name, result] of results) {
        const status = result ? '✅ PASS' : '❌ FAIL';
        console.log(`${status} ${name}`);
        if (!result) allPassed = false;
    }
    
    if (allPassed) {
        console.log('\n🎉 All checks passed! Frontend should work.');
        console.log('Start with: npm run dev');
    } else {
        console.log('\n🚨 Some checks failed. Fix these issues first.');
        console.log('\n💡 Common fixes:');
        console.log('   • Run: npm install');
        console.log('   • Check file paths');
        console.log('   • Ensure Next.js is properly configured');
    }
}

main();
