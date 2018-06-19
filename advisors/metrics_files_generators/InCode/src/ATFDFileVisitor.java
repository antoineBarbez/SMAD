import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.IBinding;
import org.eclipse.jdt.core.dom.IMethodBinding;
import org.eclipse.jdt.core.dom.IVariableBinding;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jdt.core.dom.TypeDeclaration;


public class ATFDFileVisitor extends ASTVisitor {
	private String packageName;
	
	// The text lines that should be printed in the final metrics file.
	private List<String> lines = new ArrayList<String>();
	
	public List<String> getLines () {
		return lines;
	}
	
	@Override
	public boolean visit(PackageDeclaration node) {
		packageName = node.getName().getFullyQualifiedName();
		return true;
	}
	
	@Override
	public boolean visit(TypeDeclaration node) {
		// Ignore interfaces and inner classes.
		if (node.isInterface() || node.isMemberTypeDeclaration()) {
			return true;
		}
		
		// Construct the class's name.
		String className;
		if (packageName != null) {
			className = packageName + "." + node.getName().getFullyQualifiedName();
		}else {
			className = node.getName().getFullyQualifiedName();
		}
		
		// Visit the class.
		ATFDClassVisitor visitor = new ATFDClassVisitor();
		node.accept(visitor);
		
		// Extract the lines
		Map<String, Set<String>> methodToAccessedFieldsMap = visitor.getMethodToAccessedFieldsMap();
		for (String methodName : methodToAccessedFieldsMap.keySet()) {
			Set<String>accessedFields = methodToAccessedFieldsMap.get(methodName);
			Map<String, Integer> classToNbAccessedFieldsMap = computeClassToNbAccessedFieldsMap (className, accessedFields);
			
			for (String declaringClass : classToNbAccessedFieldsMap.keySet()) {
				Integer nb = classToNbAccessedFieldsMap.get(declaringClass);
				lines.add(className + ";" + methodName + ";" + declaringClass + ";" + String.valueOf(nb));
			}
		}
		return true;
	}
	
	private Map<String, Integer> computeClassToNbAccessedFieldsMap (String embeddingClass, Set<String> accessedFields) {
		Map<String, Integer> classToNbAccessedFieldsMap = new HashMap<String, Integer>();
		for (String accessedField : accessedFields) {
			String [] accessedFieldList = accessedField.split("\\+");
			String declaringClass = accessedFieldList[0];
			
			if (!declaringClass.equals("")) {	
				int count = classToNbAccessedFieldsMap.containsKey(declaringClass) ? classToNbAccessedFieldsMap.get(declaringClass) : 0;
				classToNbAccessedFieldsMap.put(declaringClass, count + 1);
			}
		}
		
		return classToNbAccessedFieldsMap;
	}
}

class ATFDClassVisitor extends ASTVisitor {
	private Map<String, Set<String>> methodToAccessedFieldsMap = new HashMap<String, Set<String>>();
	
	public  Map<String, Set<String>> getMethodToAccessedFieldsMap () {
		return methodToAccessedFieldsMap;
	}
	
	@Override
	public boolean visit(MethodDeclaration node) {
		if (node.isConstructor() || node.getBody() == null) {
			return true;
		}
		
		// Construct the method's name.
		List<String> params = new ArrayList<>();
		for (SingleVariableDeclaration var : (List<SingleVariableDeclaration>) node.parameters()) {
			IVariableBinding varBind = var.resolveBinding();
			if (varBind == null) {
				params.add(var.toString().split("\\s+")[0]);
			}else {
				params.add(varBind.getType().getQualifiedName());
			}
		}
		Collections.sort(params, String.CASE_INSENSITIVE_ORDER);
		
		StringBuffer buffer = new StringBuffer();
		buffer.append(node.getName().getIdentifier());
		buffer.append("(");
		buffer.append(String.join(", ", params));
		buffer.append(")");

		String methodName = buffer.toString();
		
		// Visit the body of the method.
		ATFDMethodVisitor visitor = new ATFDMethodVisitor();
		node.getBody().accept(visitor);
		
		if (!methodToAccessedFieldsMap.containsKey(methodName)) {
			methodToAccessedFieldsMap.put(methodName, visitor.getAccessedFields());
		}
		
		return true;
	}
}


class ATFDMethodVisitor extends ASTVisitor {
	// Set containing all field accessed in the method's body.
	// The fields are stored like: "declaring_class_name+field_name".
	private Set<String> accessedFields = new HashSet<String>();
	
	public Set<String> getAccessedFields () {
		return accessedFields;
	}
	
	@Override
	public boolean visit(SimpleName node) {
		IBinding bind = node.resolveBinding();
		if (bind == null) {
			return true;
		}
		
		String field = null;
		String declaringClass = null;
		if (bind.getKind() == IBinding.VARIABLE) {
			IVariableBinding varBind = (IVariableBinding) bind;
			
			if (varBind.isField()) {
				field = varBind.getName();
				if (varBind.getDeclaringClass() == null) {
					return true;
				}
				
				if (varBind.getDeclaringClass().isNested()) {
					declaringClass = varBind.getDeclaringClass().getDeclaringClass().getQualifiedName();
				}else {
					declaringClass = varBind.getDeclaringClass().getQualifiedName();
				}
			}
		}else if (bind.getKind() == IBinding.METHOD) {
			IMethodBinding mBind = (IMethodBinding) bind;
			
			field = getAccessedField(mBind.getName());
			if (field == null) {
				return true;
			}
			
			if (mBind.getDeclaringClass() == null) {
				return true;
			}
			
			if (mBind.getDeclaringClass().isNested()) {
				declaringClass = mBind.getDeclaringClass().getDeclaringClass().getQualifiedName();
			}else {
				declaringClass = mBind.getDeclaringClass().getQualifiedName();
			}
		}
		
		if (declaringClass == null) {
			return true;
		}
		accessedFields.add(declaringClass + '+' + field);
		
		return true;
	}
	
	// Return the field accessed by a method if the method is an accessor.
	private String getAccessedField(String methodName) {
		String fieldName;
		if ((methodName.startsWith("get") || methodName.startsWith("set")) && methodName.length() > 3) {
			fieldName =methodName.substring(3);
		} else if (methodName.startsWith("is") && methodName.length() > 2) {
			fieldName = methodName.substring(2);
		} else {
			return null;
		}
		
		String field = Character.toLowerCase(fieldName.charAt(0)) + fieldName.substring(1);
		
		return field;
	}
}