# Feature Template Generator

## Quick Scaffold Command

```bash
# Create feature structure
mkdir -p lib/features/{feature_name}/{data/{datasources,models,repositories},domain/{entities,repositories,usecases},presentation/{viewmodels,pages,widgets}}
```

## File Templates

### Entity Template
```dart
// lib/features/{feature}/domain/entities/{name}.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part '{name}.freezed.dart';

@freezed
class {Name} with _${Name} {
  const factory {Name}({
    required String id,
    // Add fields
  }) = _{Name};
}
```

### Repository Interface Template
```dart
// lib/features/{feature}/domain/repositories/{name}_repository.dart
import 'package:dartz/dartz.dart';
import '../../../../core/error/failures.dart';
import '../entities/{name}.dart';

abstract class {Name}Repository {
  Future<Either<Failure, {Name}>> get{Name}(String id);
  Future<Either<Failure, List<{Name}>>> getAll{Name}s();
  Future<Either<Failure, void>> save{Name}({Name} item);
  Future<Either<Failure, void>> delete{Name}(String id);
}
```

### Usecase Template
```dart
// lib/features/{feature}/domain/usecases/get_{name}.dart
import 'package:dartz/dartz.dart';
import '../../../../core/error/failures.dart';
import '../entities/{name}.dart';
import '../repositories/{name}_repository.dart';

class Get{Name} {
  final {Name}Repository repository;
  
  Get{Name}(this.repository);
  
  Future<Either<Failure, {Name}>> call(String id) {
    return repository.get{Name}(id);
  }
}
```

### Model Template
```dart
// lib/features/{feature}/data/models/{name}_model.dart
import 'package:freezed_annotation/freezed_annotation.dart';
import '../../domain/entities/{name}.dart';

part '{name}_model.freezed.dart';
part '{name}_model.g.dart';

@freezed
class {Name}Model with _${Name}Model {
  const {Name}Model._();
  
  const factory {Name}Model({
    required String id,
    // Add fields matching API response
  }) = _{Name}Model;
  
  factory {Name}Model.fromJson(Map<String, dynamic> json) => 
      _${Name}ModelFromJson(json);
  
  {Name} toEntity() => {Name}(id: id);
}
```

### Repository Implementation Template
```dart
// lib/features/{feature}/data/repositories/{name}_repository_impl.dart
import 'package:dartz/dartz.dart';
import '../../../../core/error/failures.dart';
import '../../../../core/network/network_info.dart';
import '../../domain/entities/{name}.dart';
import '../../domain/repositories/{name}_repository.dart';
import '../datasources/{name}_remote_datasource.dart';
import '../datasources/{name}_local_datasource.dart';

class {Name}RepositoryImpl implements {Name}Repository {
  final {Name}RemoteDataSource remoteDataSource;
  final {Name}LocalDataSource localDataSource;
  final NetworkInfo networkInfo;

  {Name}RepositoryImpl({
    required this.remoteDataSource,
    required this.localDataSource,
    required this.networkInfo,
  });

  @override
  Future<Either<Failure, {Name}>> get{Name}(String id) async {
    if (await networkInfo.isConnected) {
      try {
        final model = await remoteDataSource.get{Name}(id);
        await localDataSource.cache{Name}(model);
        return Right(model.toEntity());
      } on ServerException {
        return Left(ServerFailure());
      }
    } else {
      try {
        final model = await localDataSource.getCached{Name}(id);
        return Right(model.toEntity());
      } on CacheException {
        return Left(CacheFailure());
      }
    }
  }
}
```

### ViewModel Template (Riverpod)
```dart
// lib/features/{feature}/presentation/viewmodels/{name}_viewmodel.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import '../../domain/entities/{name}.dart';
import '../../domain/usecases/get_{name}.dart';
import '../../../../core/di/injection.dart';

part '{name}_viewmodel.freezed.dart';

@freezed
class {Name}State with _${Name}State {
  const factory {Name}State.initial() = _Initial;
  const factory {Name}State.loading() = _Loading;
  const factory {Name}State.loaded({Name} data) = _Loaded;
  const factory {Name}State.error(String message) = _Error;
}

class {Name}Notifier extends StateNotifier<{Name}State> {
  final Get{Name} _get{Name};
  
  {Name}Notifier(this._get{Name}) : super(const {Name}State.initial());
  
  Future<void> load(String id) async {
    state = const {Name}State.loading();
    final result = await _get{Name}(id);
    result.fold(
      (failure) => state = {Name}State.error(failure.message),
      (data) => state = {Name}State.loaded(data),
    );
  }
}

final {name}Provider = StateNotifierProvider<{Name}Notifier, {Name}State>(
  (ref) => {Name}Notifier(getIt<Get{Name}>()),
);
```
