import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.TypeDeclaration;

public class FileVisitor extends ASTVisitor {
	private String packageName;
	
	private List<String> types =  new ArrayList<String>();
	private Set<String> staticEntities = new HashSet<String>();
	private Map<String, String> accessorToAccessedFieldMap = new LinkedHashMap<String,String>();
	private Map<String, Set<String>> classToEntitySetMap = new LinkedHashMap<String,Set<String>>();
	private Map<String, Set<String>> methodToEntitySetMap = new LinkedHashMap<String,Set<String>>();
	private Map<String, Set<String>> methodToTargetClassSetMap = new LinkedHashMap<String,Set<String>>();
	
	public Map<String, Set<String>> getClassToEntitySetMap() {
		return this.classToEntitySetMap;
	}
	
	public Map<String, Set<String>> getMethodToEntitySetMap() {
		return this.methodToEntitySetMap;
	}
	
	public Map<String,Set<String>> getMethodToTargetClassSetMap() {
		return this.methodToTargetClassSetMap;
	}
	
	public List<String> getTypes() {
		return this.types;
	}
	
	public Set<String> getStaticEntities() {
		return this.staticEntities;
	}
	
	public Map<String, String> getaccessorToAccessedFieldMap() {
		return this.accessorToAccessedFieldMap;
	}
	
	@Override
	public boolean visit(PackageDeclaration node) {
		packageName = node.getName().getFullyQualifiedName();
		return true;
	}
	
	@Override
	public boolean visit(TypeDeclaration node) {
		// Construct the class's name.
		String typeName;
		if (packageName != null) {
			typeName = packageName + "." + node.getName().getFullyQualifiedName();
		}else {
			typeName = node.getName().getFullyQualifiedName();
		}
		types.add(typeName);
		
		// Ignore interfaces and inner classes.
		if (node.isInterface() || node.isMemberTypeDeclaration()) {
			return true;
		}
		
		// Visit the class.
		ClassVisitor visitor = new ClassVisitor(typeName);
		node.accept(visitor);
		
		classToEntitySetMap.put(typeName, visitor.getEntitySet());
		methodToEntitySetMap.putAll(visitor.getMethodToEntitySetMap());
		methodToTargetClassSetMap.putAll(visitor.getMethodToTargetClassSetMap());
		staticEntities.addAll(visitor.getStaticEntities());
		accessorToAccessedFieldMap.putAll(visitor.getaccessorToAccessedFieldMap());
		return true;
	}
}