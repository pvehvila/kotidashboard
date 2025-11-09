# Päivitä pip
Write-Host "Updating pip..."
python -m pip install --upgrade pip

# Asenna/päivitä riippuvuudet
Write-Host "Installing/updating dependencies..."
pip install -r requirements.txt

# Asenna kehitystyökalut
Write-Host "Installing development tools..."
pip install ruff pytest pytest-cov

Write-Host "Dependencies updated successfully!"
