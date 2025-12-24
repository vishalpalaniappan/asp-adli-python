[iteration v1]

Software systems are the realization of an intentional design. This means that the relationship between every abstraction in the system is established through the design. The programming language used to implement the design must have the ability to establish the necessary relationships and realize the intention of the design. On a low level, this means being able to implement the mechanical abstractions using control flow, loops etc. On a higher level, it means respecting the semantic rules and relationships by shaping how data and intention is moved between them. Ultimately, the successful operation of a software system hinges on the ability to realize the intentions of its design in the environment that it is operating in.

Debugging a software system is about understanding how the system was unable to realize the intentions of its design and understanding how to realign its reality with its intention. The misalignment can result in a loud failure that ends in an exception or it can simply be the world not being realized as intended. To illustrate this concept, the following sample design is used:

![library-manager]

This design realizes a library manager that provides the user with a menu to interact with it. The user can submit books which are added to a basket. When the user decides to place the books on the shelf, it takes each book from the basket and places it on the shelf using the first letter of the name as the slot. It also provides an option to display the contents of the library and exit the library manager.

Since the world is intentionally designed through the semantic relationships established through the design, a failure to respect these intentions results in predictable failure modalities that can be resolved by realigning the behavior of the design with its intentions. 

For example, if a system intends to use the first letter of a book’s name to place it on the shelf, then accepting a book with no name establishes the root cause of an inevitable failure in this intentionally designed world. The design semantics establish a constraint on the book name for the intention of the design to be successfully realized. 

However, the failure to respect the intention of the design doesn’t necessarily end in a loud failure as expressed by the generated exception. It can simply manifest as the world not realizing itself as intended. For example, the library manager intends to accept a book and place it in the basket. If this intention is not respected, then when it attempts to place the books on the shelf, it won’t be able to. This won’t result in a failure, instead, the design will simply see that there are no books in the basket. In this case, the root cause is a failure to respect the intentions of the design. 

While one ended in a mechanical failure and the other did not, at the semantic level, both failed to realize the design's intentions. In this sense, a semantic failure can result in a mechanical failure but it doesn’t have to. Regardless, at the semantic layer is meaningful, and a failure to respect the intentions of the design establishes predictable failure modalities and defines precise resolution strategies. By instrumenting the design semantics onto the implementation, the misalignment between reality and intention can automatically understood and ultimately, this process automates debugging.

[library-manager]: ./library_manager_v2.png
