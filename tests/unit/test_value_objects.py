"""
Unit Tests for Value Objects
Demonstrates testability of domain layer
"""

import pytest
from domain.value_objects.email import Email
from domain.value_objects.file_id import FileId
from domain.value_objects.permission_id import PermissionId
from domain.value_objects.permission_role import PermissionRole


class TestEmail:
    """Test Email value object"""
    
    def test_valid_email_creation(self):
        """Test creating valid email"""
        email = Email("user@example.com")
        assert email.value == "user@example.com"
        assert email.domain == "example.com"
    
    def test_email_normalization(self):
        """Test email normalization (lowercase, strip)"""
        email = Email("  User@EXAMPLE.COM  ")
        assert email.value == "user@example.com"
    
    def test_invalid_email_raises_error(self):
        """Test invalid email raises ValueError"""
        with pytest.raises(ValueError, match="Invalid email"):
            Email("invalid-email")
        
        with pytest.raises(ValueError):
            Email("@example.com")
        
        with pytest.raises(ValueError):
            Email("user@")
    
    def test_email_equality(self):
        """Test email equality comparison"""
        email1 = Email("user@example.com")
        email2 = Email("USER@EXAMPLE.COM")
        email3 = Email("other@example.com")
        
        assert email1 == email2  # Case-insensitive
        assert email1 != email3
    
    def test_email_hashable(self):
        """Test email can be used in sets/dicts"""
        email1 = Email("user@example.com")
        email2 = Email("user@example.com")
        
        email_set = {email1, email2}
        assert len(email_set) == 1  # Duplicates removed
    
    def test_empty_email_raises_error(self):
        """Test empty email raises error"""
        with pytest.raises(ValueError):
            Email("")
        
        with pytest.raises(ValueError):
            Email("   ")


class TestFileId:
    """Test FileId value object"""
    
    def test_valid_file_id_creation(self):
        """Test creating valid file ID"""
        file_id = FileId("1a2b3c4d5e6f")
        assert file_id.value == "1a2b3c4d5e6f"
    
    def test_file_id_normalization(self):
        """Test file ID normalization"""
        file_id = FileId("  ABC123  ")
        assert file_id.value == "ABC123"
    
    def test_empty_file_id_raises_error(self):
        """Test empty file ID raises error"""
        with pytest.raises(ValueError, match="File ID cannot be empty"):
            FileId("")
        
        with pytest.raises(ValueError):
            FileId("   ")
    
    def test_file_id_equality(self):
        """Test file ID equality"""
        id1 = FileId("abc123")
        id2 = FileId("abc123")
        id3 = FileId("xyz789")
        
        assert id1 == id2
        assert id1 != id3
    
    def test_file_id_string_representation(self):
        """Test file ID string conversion"""
        file_id = FileId("test123")
        assert str(file_id) == "test123"


class TestPermissionId:
    """Test PermissionId value object"""
    
    def test_valid_permission_id_creation(self):
        """Test creating valid permission ID"""
        perm_id = PermissionId("perm_123")
        assert perm_id.value == "perm_123"
    
    def test_permission_id_normalization(self):
        """Test permission ID normalization"""
        perm_id = PermissionId("  PERM_ABC  ")
        assert perm_id.value == "PERM_ABC"
    
    def test_empty_permission_id_raises_error(self):
        """Test empty permission ID raises error"""
        with pytest.raises(ValueError, match="Permission ID cannot be empty"):
            PermissionId("")


class TestPermissionRole:
    """Test PermissionRole enum"""
    
    def test_role_values(self):
        """Test permission role enum values"""
        assert PermissionRole.OWNER.value == "owner"
        assert PermissionRole.WRITER.value == "writer"
        assert PermissionRole.COMMENTER.value == "commenter"
        assert PermissionRole.READER.value == "reader"
    
    def test_role_from_string(self):
        """Test creating role from string"""
        role = PermissionRole.from_string("owner")
        assert role == PermissionRole.OWNER
        
        role = PermissionRole.from_string("WRITER")
        assert role == PermissionRole.WRITER
    
    def test_invalid_role_raises_error(self):
        """Test invalid role string raises error"""
        with pytest.raises(ValueError, match="Invalid permission role"):
            PermissionRole.from_string("invalid")
    
    def test_role_display_name(self):
        """Test role display names"""
        assert PermissionRole.OWNER.display_name == "Owner"
        assert PermissionRole.WRITER.display_name == "Editor"
        assert PermissionRole.READER.display_name == "Viewer"
    
    def test_can_edit(self):
        """Test can_edit property"""
        assert PermissionRole.OWNER.can_edit is True
        assert PermissionRole.WRITER.can_edit is True
        assert PermissionRole.COMMENTER.can_edit is False
        assert PermissionRole.READER.can_edit is False
    
    def test_role_comparison(self):
        """Test role equality"""
        assert PermissionRole.OWNER == PermissionRole.OWNER
        assert PermissionRole.OWNER != PermissionRole.READER


# Test fixtures for reuse
@pytest.fixture
def sample_email():
    """Sample email for testing"""
    return Email("test@example.com")


@pytest.fixture
def sample_file_id():
    """Sample file ID for testing"""
    return FileId("file_12345")


@pytest.fixture
def sample_permission_id():
    """Sample permission ID for testing"""
    return PermissionId("perm_67890")


class TestValueObjectIntegration:
    """Integration tests for value objects"""
    
    def test_value_objects_in_dictionary(self, sample_email, sample_file_id):
        """Test value objects as dictionary keys"""
        data = {
            sample_email: "user data",
            sample_file_id: "file data"
        }
        
        # Should work with same values
        assert data[Email("test@example.com")] == "user data"
        assert data[FileId("file_12345")] == "file data"
    
    def test_value_objects_immutability(self, sample_email):
        """Test value objects are immutable"""
        # Value objects should not have setters
        with pytest.raises(AttributeError):
            sample_email.value = "new@example.com"  # type: ignore
